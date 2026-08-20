#!/usr/bin/env python3
"""
Magento gift cards  →  Shopify Gift Cards (Admin GraphQL API, Option B)

Unlike every other *_shopify.py script in this folder, this one does NOT
produce a Matrixify CSV — Matrixify cannot import Gift Cards directly (the
Gift Card API is app-scoped, not template-scoped). Instead it calls the
Admin GraphQL `giftCardCreate` mutation directly, one call per card, so
that the **existing Magento code is preserved** (Option B — see
05_DOCS/import/gift-cards.md for why Option A, importing Orders with a
Gift Card line item, was rejected: it issues brand-new codes and would
require re-contacting all 281 cardholders).

Scope: only cards with Card Status == '1' (active, confirmed by client)
and a positive balance. Used cards (status '2') already have a zero
practical value and are not migrated.

Routing: a card can list several Magento store views in `Store Code`
(comma-separated). Store views starting with eu_/ww_ → Dandoy-Sports,
bt_ → Butterfly TT, 'ALL' → both. A card touching both brands is created
in both shops (mirrors how shared products/customers are duplicated
elsewhere in this pipeline) — 5 cards fall into this case.

Safety: dry-run by default. Nothing is sent to Shopify unless --execute
is passed AND the matching credentials are present in the environment.
A gift card is real stored value — there is no bulk-delete equivalent to
the *_PURGE.csv mechanism used for products/orders, so mistakes here are
not easily reversible.

Usage:
    python3 migrate_giftcards_shopify.py --shop dandoy               # dry-run
    python3 migrate_giftcards_shopify.py --shop dandoy --execute      # live
    python3 migrate_giftcards_shopify.py --shop both --execute --limit 5

Credentials (Dev Dashboard app, scope `write_gift_cards`): a static offline access token,
obtained via the Authorization Code Grant flow (NOT Client Credentials Grant — CCG is
restricted to development stores only and always fails with `shop_not_permitted` on a paid
production store like dandoy-sports, confirmed 5 août 2026). Use
`get_shopify_access_token.py` once per store to run that OAuth flow and write the token
straight into the env file (never printed to stdout/chat):

    SHOPIFY_DANDOY_STORE_DOMAIN      e.g. dandoy-sports.myshopify.com
    SHOPIFY_DANDOY_ACCESS_TOKEN
    SHOPIFY_BUTTERFLY_STORE_DOMAIN
    SHOPIFY_BUTTERFLY_ACCESS_TOKEN
"""

import argparse
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.request

INPUT_GIFTCARDS = '/home/gregory/Documents/Labo/dandoy/01_DATA_RAW/gift_cards_export_file.csv'
REPORT_PATH = '/home/gregory/Documents/Labo/dandoy/04_SHOPIFY_IMPORTS/giftcards_migration_report_{shop}.csv'

API_VERSION = '2025-01'
REQUEST_DELAY_SECONDS = 0.5  # generous margin under the GraphQL cost limit for ~281 single-object creates

STORE_ENV = {
    'dandoy':    ('SHOPIFY_DANDOY_STORE_DOMAIN', 'SHOPIFY_DANDOY_ACCESS_TOKEN'),
    'butterfly': ('SHOPIFY_BUTTERFLY_STORE_DOMAIN', 'SHOPIFY_BUTTERFLY_ACCESS_TOKEN'),
}

MUTATION = """
mutation giftCardCreate($input: GiftCardCreateInput!) {
  giftCardCreate(input: $input) {
    giftCard { id balance { amount currencyCode } }
    giftCardCode
    userErrors { field message code }
  }
}
"""

CUSTOMER_LOOKUP_QUERY = """
query($q: String!) {
  customers(first: 1, query: $q) {
    edges { node { id } }
  }
}
"""


def brand_scope(store_code):
    """Magento Store Code(s) -> set of {'dandoy', 'butterfly'} this card belongs to."""
    scopes = set()
    for code in (store_code or '').split(','):
        code = code.strip()
        if code == 'ALL':
            scopes |= {'dandoy', 'butterfly'}
        elif code.startswith('eu_') or code.startswith('ww_'):
            scopes.add('dandoy')
        elif code.startswith('bt_'):
            scopes.add('butterfly')
    return scopes or {'dandoy'}  # no known active card is missing Store Code, but fail safe


def load_active_cards():
    with open(INPUT_GIFTCARDS, encoding='utf-8') as f:
        rows = [r for r in csv.DictReader(f) if r.get('Card ID')]

    cards = []
    for r in rows:
        if r['Card Status'] != '1':
            continue
        balance = float(r['Card Balance'] or 0)
        if balance <= 0:
            continue
        cards.append(r)
    return cards


def build_jobs(cards, shop_filter):
    """One job per (card, shop) pair, already filtered to shop_filter."""
    jobs = []
    for r in cards:
        for shop in brand_scope(r['Store Code']):
            if shop_filter != 'both' and shop != shop_filter:
                continue
            jobs.append({
                'shop': shop,
                'code': r['Card Code'],
                'balance': f"{float(r['Card Balance']):.2f}",
                'currency': r['Card Currency'] or 'EUR',
                'recipient_email': r['User Email'].strip().lower() if r['User Email'] else '',
                'note': (
                    f"Migré depuis Magento (Card ID {r['Card ID']}) — "
                    f"De: {r['Mail From'] or '?'} — "
                    f"À: {r['Mail To'] or '?'} <{r['User Email'] or '?'}>"
                ).strip(),
                'created_date': r['Created Date'],
            })
    return jobs


def find_customer_id(domain, token, email):
    if not email:
        return None
    resp = call_shopify(domain, token, CUSTOMER_LOOKUP_QUERY, {'q': f'email:{email}'})
    edges = resp.get('data', {}).get('customers', {}).get('edges', [])
    return edges[0]['node']['id'] if edges else None


def call_shopify(domain, token, query, variables):
    url = f"https://{domain}/admin/api/{API_VERSION}/graphql.json"
    body = json.dumps({'query': query, 'variables': variables}).encode('utf-8')
    req = urllib.request.Request(url, data=body, method='POST', headers={
        'Content-Type': 'application/json',
        'X-Shopify-Access-Token': token,
    })
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode('utf-8'))


def migrate(shop, jobs, execute, limit):
    domain_var, token_var = STORE_ENV[shop]
    domain = os.environ.get(domain_var)
    token = os.environ.get(token_var)

    if execute and not (domain and token):
        print(f"  [{shop}] ERREUR: {domain_var} et/ou {token_var} manquants dans l'environnement — abandon.")
        return []

    shop_jobs = [j for j in jobs if j['shop'] == shop][:limit] if limit else [j for j in jobs if j['shop'] == shop]
    results = []

    for i, job in enumerate(shop_jobs, 1):
        row = {
            'card_code': job['code'],
            'balance': job['balance'],
            'currency': job['currency'],
            'recipient_email': job['recipient_email'],
            'matched_customer_id': '',
            'status': '',
            'shopify_gift_card_id': '',
            'error': '',
        }

        if not execute:
            row['status'] = 'DRY-RUN'
            results.append(row)
            continue

        try:
            customer_id = find_customer_id(domain, token, job['recipient_email'])
        except (urllib.error.HTTPError, urllib.error.URLError) as e:
            customer_id = None  # lookup failure shouldn't block the gift card itself
            print(f"  [{shop}] avertissement: recherche client échouée pour {job['recipient_email']} ({e})")
        row['matched_customer_id'] = customer_id or ''

        variables = {'input': {
            'initialValue': job['balance'],
            'code': job['code'],
            'note': job['note'],
        }}
        if customer_id:
            variables['input']['customerId'] = customer_id

        try:
            resp = call_shopify(domain, token, MUTATION, variables)
        except urllib.error.HTTPError as e:
            row['status'] = 'ERROR'
            row['error'] = f"HTTP {e.code}: {e.read().decode('utf-8', 'ignore')[:300]}"
            results.append(row)
            continue
        except urllib.error.URLError as e:
            row['status'] = 'ERROR'
            row['error'] = str(e)
            results.append(row)
            continue

        if resp.get('errors'):
            row['status'] = 'ERROR'
            row['error'] = json.dumps(resp['errors'])[:300]
            results.append(row)
            continue

        payload = resp['data']['giftCardCreate']
        user_errors = payload.get('userErrors') or []
        if user_errors:
            row['status'] = 'ERROR'
            row['error'] = '; '.join(f"{e.get('field')}: {e['message']}" for e in user_errors)
        else:
            row['status'] = 'CREATED'
            row['shopify_gift_card_id'] = payload['giftCard']['id']

        results.append(row)
        print(f"  [{shop}] {i}/{len(shop_jobs)} {job['code']} -> {row['status']}"
              + (f" ({row['error']})" if row['error'] else ''))
        time.sleep(REQUEST_DELAY_SECONDS)

    return results


def write_report(shop, results):
    path = REPORT_PATH.format(shop=shop)
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['card_code', 'balance', 'currency', 'recipient_email', 'matched_customer_id', 'status', 'shopify_gift_card_id', 'error'])
        w.writeheader()
        w.writerows(results)
    print(f"  Rapport écrit : {path} ({len(results)} lignes)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--shop', choices=['dandoy', 'butterfly', 'both'], required=True)
    ap.add_argument('--execute', action='store_true', help="Envoie réellement les cartes à Shopify (sinon dry-run)")
    ap.add_argument('--limit', type=int, default=0, help="Limiter le nombre de cartes par boutique (0 = toutes)")
    args = ap.parse_args()

    cards = load_active_cards()
    jobs = build_jobs(cards, args.shop)
    shops = ['dandoy', 'butterfly'] if args.shop == 'both' else [args.shop]

    total_by_shop = {s: len([j for j in jobs if j['shop'] == s]) for s in shops}
    print(f"Cartes actives chargées : {len(cards)}")
    for s in shops:
        print(f"  -> {s}: {total_by_shop[s]} carte(s) à créer" + (" (dry-run)" if not args.execute else ""))

    if not args.execute:
        print("\nMode dry-run (par défaut) — rien n'est envoyé à Shopify. Ajoutez --execute pour migrer réellement.\n")

    for s in shops:
        print(f"\n=== {s} ===")
        results = migrate(s, jobs, args.execute, args.limit)
        write_report(s, results)


if __name__ == '__main__':
    main()
