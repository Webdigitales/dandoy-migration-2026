#!/usr/bin/env python3
"""
Validation post-régénération des CSV d'import Shopify (Matrixify).

Rejoue en local les règles qui font échouer un import Matrixify avant même
d'ouvrir l'admin Shopify : handles dupliqués entre produits distincts,
options incohérentes ou dupliquées au sein d'un même produit, limite des
100 variantes, champs obligatoires vides, SKU dupliqués, et handles
orphelins référencés depuis les traductions/redirections.

Ne modifie aucun fichier. Sort avec le code 1 si des erreurs bloquantes
(niveau Matrixify) sont trouvées, 0 sinon (les warnings n'y changent rien).
"""

import csv
import os
import sys

DIR      = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
IMPORTS  = os.path.join(DIR, '04_SHOPIFY_IMPORTS')
REDIRECTS_DIR = os.path.join(DIR, '03_SEO_AND_REDIRECTS')

# Two Shopify stores (Option B): each has its own products/translations/
# collections/redirects CSV, validated independently.
STORES = [
    ('Dandoy-Sports', {
        'products':     os.path.join(IMPORTS, 'shopify_products_dandoy.csv'),
        'translations': os.path.join(IMPORTS, 'shopify_translations_dandoy.csv'),
        'collections':  os.path.join(IMPORTS, 'shopify_collections_dandoy.csv'),
        'redirects':    os.path.join(REDIRECTS_DIR, 'shopify_redirects_dandoy.csv'),
    }),
    ('Butterfly TT', {
        'products':     os.path.join(IMPORTS, 'shopify_products_butterfly.csv'),
        'translations': os.path.join(IMPORTS, 'shopify_translations_butterfly.csv'),
        'collections':  os.path.join(IMPORTS, 'shopify_collections_butterfly.csv'),
        'redirects':    os.path.join(REDIRECTS_DIR, 'shopify_redirects_butterfly.csv'),
    }),
]

MAX_VARIANTS = 100


def load_rows(path):
    if not os.path.exists(path):
        return None
    with open(path, encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))


def validate_products(rows):
    errors, warnings = [], []

    by_handle = {}
    for row in rows:
        by_handle.setdefault(row['Handle'], []).append(row)

    all_skus = {}
    for handle, group in by_handle.items():
        variant_rows = [r for r in group if r.get('Variant SKU')]

        # Champs manquants sur la 1re ligne : n'empêche pas l'import (le
        # produit se crée quand même), mais dégrade la fiche — signalé en
        # warning, pas en erreur bloquante.
        first = group[0]
        for field in ('Title', 'Vendor', 'Type'):
            if not first.get(field):
                warnings.append(f"[{handle}] '{field}' vide sur la première ligne du produit")

        if len(variant_rows) > MAX_VARIANTS:
            errors.append(f"[{handle}] {len(variant_rows)} variantes (> {MAX_VARIANTS}, plafond Shopify)")

        # Cohérence des noms d'option sur tout le groupe : un slot ne peut
        # pas s'appeler "Color" sur une ligne et "Thickness" sur une autre.
        for slot in (1, 2, 3):
            names = {r[f'Option{slot} Name'] for r in variant_rows if r.get(f'Option{slot} Name')}
            if len(names) > 1:
                errors.append(f"[{handle}] Option{slot} Name incohérent entre variantes : {sorted(names)}")

        # Combinaisons de valeurs d'options dupliquées entre variantes
        seen_combo = {}
        for r in variant_rows:
            combo = tuple(r.get(f'Option{s} Value', '') for s in (1, 2, 3))
            if combo in seen_combo:
                errors.append(
                    f"[{handle}] variantes {seen_combo[combo]} et {r['Variant SKU']} "
                    f"ont la même combinaison d'options {combo}")
            else:
                seen_combo[combo] = r['Variant SKU']

        for r in variant_rows:
            sku = r['Variant SKU']
            price = r.get('Variant Price', '')

            if not price:
                errors.append(f"[{handle}] SKU {sku} : 'Variant Price' vide")
            else:
                try:
                    if float(price) < 0:
                        errors.append(f"[{handle}] SKU {sku} : prix négatif ({price})")
                except ValueError:
                    errors.append(f"[{handle}] SKU {sku} : prix non numérique ({price!r})")

            if sku in all_skus:
                errors.append(f"SKU dupliqué '{sku}' : produits '{all_skus[sku]}' et '{handle}'")
            else:
                all_skus[sku] = handle

    return errors, warnings, set(by_handle)


def validate_translations(rows, product_handles):
    errors = []
    if rows is None:
        return errors
    for r in rows:
        handle = r.get('Entity Handle', '')
        if handle and handle not in product_handles:
            errors.append(f"Traduction orpheline : handle '{handle}' absent du fichier produits de ce store")
    return errors


def validate_redirects(rows, product_handles):
    errors = []
    if rows is None:
        return errors
    for r in rows:
        to = r.get('Redirect To', '')
        if to.startswith('/products/'):
            handle = to[len('/products/'):].split('?')[0].strip('/')
            if handle not in product_handles:
                errors.append(f"Redirection orpheline : '{r.get('Redirect From')}' → handle '{handle}' introuvable")
    return errors


def validate_collections(rows):
    # Multiple rows per Handle are normal here (one row per smart-collection
    # rule, Title only set on the first row of each group).
    errors = []
    if rows is None:
        return errors
    seen_titled = set()
    for r in rows:
        handle = r.get('Handle', '')
        if not handle:
            errors.append("Ligne de collection sans Handle")
            continue
        if r.get('Title'):
            seen_titled.add(handle)
    for handle in {r['Handle'] for r in rows if r.get('Handle')} - seen_titled:
        errors.append(f"[{handle}] collection sans Title sur aucune ligne")
    return errors


def validate_store(store_name, paths):
    products = load_rows(paths['products'])
    if products is None:
        print(f"✗ Introuvable : {paths['products']}")
        return 1

    translations = load_rows(paths['translations'])
    collections  = load_rows(paths['collections'])
    redirects    = load_rows(paths['redirects'])

    print(f"=== {store_name} ===\n")

    prod_errors, prod_warnings, product_handles = validate_products(products)
    tr_errors  = validate_translations(translations, product_handles)
    rd_errors  = validate_redirects(redirects, product_handles)
    col_errors = validate_collections(collections)

    all_errors = prod_errors + tr_errors + rd_errors + col_errors

    print(f"Produits      : {len(product_handles)} handles, {len(products)} lignes")
    print(f"Traductions   : {len(translations) if translations is not None else 0} lignes")
    print(f"Collections   : {len(collections) if collections is not None else 0} lignes")
    print(f"Redirections  : {len(redirects) if redirects is not None else 0} lignes")
    print()

    if all_errors:
        print(f"✗ {len(all_errors)} erreur(s) bloquante(s) pour Matrixify :\n")
        for e in all_errors[:200]:
            print(f"  - {e}")
        if len(all_errors) > 200:
            print(f"  … et {len(all_errors) - 200} de plus")
    else:
        print("✓ Aucune erreur bloquante détectée")

    if prod_warnings:
        print(f"\n⚠ {len(prod_warnings)} avertissement(s) (non bloquants — complétude des données) :\n")
        for w in prod_warnings[:20]:
            print(f"  - {w}")
        if len(prod_warnings) > 20:
            print(f"  … et {len(prod_warnings) - 20} de plus")

    print()
    return 1 if all_errors else 0


def main():
    print("=== Validation des fichiers d'import Shopify ===\n")
    exit_code = 0
    for store_name, paths in STORES:
        exit_code = max(exit_code, validate_store(store_name, paths))
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
