#!/bin/bash
# Régénère tous les fichiers d'import Shopify + fichiers de purge
# À lancer après mise à jour de 01_DATA_RAW/export_magento_products_all.csv

set -e
DIR="$(cd "$(dirname "$0")/../.." && pwd)"
SCRIPTS="$DIR/02_ANALYSIS_AND_MAPPING/SCRIPTS"

echo "=== Régénération complète ==="
echo "Source: $DIR/01_DATA_RAW/export_magento_products_all.csv"
echo ""

echo "[1/8] Produits + traductions..."
python3 "$SCRIPTS/magento_to_shopify.py"
echo ""

echo "[2/8] Collections..."
python3 "$SCRIPTS/generate_collections.py"
echo ""

echo "[3/8] Redirections..."
python3 "$SCRIPTS/generate_redirects.py"
echo ""

echo "[4/8] Customers..."
python3 "$SCRIPTS/magento_to_shopify_customers.py"
echo ""

echo "[5/8] Commandes 2025-2026..."
python3 "$SCRIPTS/magento_to_shopify_orders.py"
echo ""

echo "[6/8] Sample (par boutique)..."
python3 - << 'SAMPLEEOF'
import csv, os

base = os.environ.get('DIR', '.')
imports = os.path.join(base, '04_SHOPIFY_IMPORTS')

targets = [
    ('Blades', 'Handle', None), ('Rubbers', 'Color', 'Thickness'),
    ('Clothing', 'Size', None), ('Shoes', 'Size', None),
    ('Bags', 'Color', None), ('Balls', 'Quantity', None),
    ('Cleaners', 'Quantity', None), ('Tables and Nets', 'Color', None),
    ('Accessories', 'Title', None), ('Blades', 'Title', None),
]

def build_sample(store_suffix):
    src = os.path.join(imports, f'shopify_products_{store_suffix}.csv')
    with open(src, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        all_rows = list(reader)
        fieldnames = reader.fieldnames

    handles, seen = [], set()
    for want_type, want_o1, want_o2 in targets:
        for r in all_rows:
            if not r.get('Title') or r['Handle'] in seen:
                continue
            if r.get('Type') == want_type and r.get('Option1 Name') == want_o1:
                if want_o2 is None or r.get('Option2 Name') == want_o2:
                    seen.add(r['Handle'])
                    handles.append(r['Handle'])
                    break

    sample = [r for r in all_rows if r['Handle'] in handles]
    dest = os.path.join(imports, f'shopify_products_sample_{store_suffix}.csv')
    with open(dest, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(sample)
    print(f"  {store_suffix}: {len(handles)} produits, {len(sample)} lignes")

build_sample('dandoy')
build_sample('butterfly')
SAMPLEEOF
echo ""

echo "[7/8] Fichiers de purge (par boutique)..."
python3 - << 'PYEOF'
import csv, os

base = os.environ.get('DIR', '.')
imports = os.path.join(base, '04_SHOPIFY_IMPORTS')
redirects_dir = os.path.join(base, '03_SEO_AND_REDIRECTS')

def purge_handles(src_path, dest_path):
    handles, seen = [], set()
    with open(src_path, encoding='utf-8') as f:
        for row in csv.DictReader(f):
            h = row.get('Handle', '')
            if h and h not in seen:
                seen.add(h)
                handles.append(h)
    with open(dest_path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['Command', 'Handle'])
        w.writeheader()
        for h in handles:
            w.writerow({'Command': 'DELETE', 'Handle': h})
    return len(handles)

def purge_redirects(src_path, dest_path):
    with open(src_path, encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    with open(dest_path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['Command', 'Redirect From', 'Redirect To'])
        w.writeheader()
        for r in rows:
            w.writerow({'Command': 'DELETE', 'Redirect From': r['Redirect From'], 'Redirect To': r['Redirect To']})
    return len(rows)

for suffix in ('dandoy', 'butterfly'):
    n_products = purge_handles(
        os.path.join(imports, f'shopify_products_{suffix}.csv'),
        os.path.join(imports, f'shopify_products_{suffix}_PURGE.csv'))
    n_collections = purge_handles(
        os.path.join(imports, f'shopify_collections_{suffix}.csv'),
        os.path.join(imports, f'shopify_collections_{suffix}_PURGE.csv'))
    n_redirects = purge_redirects(
        os.path.join(redirects_dir, f'shopify_redirects_{suffix}.csv'),
        os.path.join(imports, f'shopify_redirects_{suffix}_PURGE.csv'))
    print(f"  {suffix}: {n_products} produits, {n_collections} collections, {n_redirects} redirections")
PYEOF

echo ""
echo "[8/8] Validation..."
set +e
python3 "$SCRIPTS/validate_shopify_csv.py"
VALIDATION_EXIT=$?
set -e

echo ""
echo "=== Terminé ==="
echo "Fichiers dans 04_SHOPIFY_IMPORTS/ et 03_SEO_AND_REDIRECTS/"
if [ "$VALIDATION_EXIT" -ne 0 ]; then
    echo ""
    echo "⚠ La validation a détecté des erreurs bloquantes — voir le détail ci-dessus avant tout import Matrixify."
fi
exit "$VALIDATION_EXIT"
