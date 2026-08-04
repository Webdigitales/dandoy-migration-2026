#!/usr/bin/env python3
"""
Stratified sample of Magento orders → Shopify orders CSV (Matrixify format).

Unlike the 5-order sample in regenerate_all.sh (just the first 5 orders per
store, used for the initial column-mapping tests), this pulls a mix of edge
cases across the full 39k-order dataset that the 5-order sample can't cover:
currency conversion, pending/partial payment, partial shipment (no
Fulfillment Line), large orders, every payment gateway, and Sendcloud relay
points. Target: under 1000 total orders.

Reuses build_rows()/SHOPIFY_COLS from magento_to_shopify_orders.py so the
transformation logic (tax, discount, fulfillment, Note…) is identical to
the full production file — this is a slice of the same data, not a
different pipeline.

Output: shopify_orders_stratified_{dandoy|butterfly}.csv (not versioned —
regenerate from 01_DATA_RAW/export_order_all_2025_2026.csv as needed).
"""

import csv
import random

import magento_to_shopify_orders as base

INPUT             = base.INPUT
OUTPUT_DANDOY     = '/home/gregory/Documents/Labo/dandoy/04_SHOPIFY_IMPORTS/shopify_orders_stratified_dandoy.csv'
OUTPUT_BUTTERFLY  = '/home/gregory/Documents/Labo/dandoy/04_SHOPIFY_IMPORTS/shopify_orders_stratified_butterfly.csv'
TARGET_MAX        = 950
SEED              = 20260804

# Payment methods with far fewer orders than Mollie's ~35k — under-sampled
# by a handful of consecutive orders, so each gateway (and its Note-field
# behavior — no transaction ID captured for these, unlike Mollie) gets
# checked, not just the majority path.
NON_MOLLIE_METHODS = (
    'payplug_payments_standard', 'payplug_payments_ideal',
    'payplug_payments_bancontact', 'mollie_methods_klarna',
    'mollie_methods_klarnapaylater', 'paypal_express', 'free',
)
MOLLIE_METHODS = (
    'mollie_methods_creditcard', 'mollie_methods_paypal',
    'mollie_methods_bancontact', 'mollie_methods_ideal',
)


def categorize(rows):
    cats = {
        'fx': [], 'pending': [], 'refunded': [], 'not_full_shipped': [],
        'large': [], 'sendcloud': [], 'by_store': {}, 'by_payment': {},
    }
    for row in rows:
        inc = row['Increment Id'].strip()

        rate = base.fx_rate(row)
        if rate != 1.0:
            cats['fx'].append(inc)

        due = base.parse_float(row.get('Total Due'))
        refunded = base.parse_float(row.get('Subtotal Refunded'))
        if refunded > 0:
            cats['refunded'].append(inc)
        elif due > 0:
            cats['pending'].append(inc)

        n = 0
        statuses = []
        for i in range(1, base.MAX_ITEMS + 12):
            sku = (row.get(f'item {i}(Sku)') or '').strip()
            if not sku:
                break
            n += 1
            statuses.append((row.get(f'item {i}(Status)') or '').strip())
        if statuses and not all(s == 'Shipped' for s in statuses):
            cats['not_full_shipped'].append(inc)
        if n >= 10:
            cats['large'].append(inc)

        if (row.get('Sendcloud Service Point Name') or '').strip():
            cats['sendcloud'].append(inc)

        store = row.get('Store Name', '').strip()
        cats['by_store'].setdefault(store, []).append(inc)

        pm = row.get('Payment Method', '').strip()
        cats['by_payment'].setdefault(pm, []).append(inc)

    return cats


def pick(rng, pool, n):
    return set(rng.sample(pool, min(n, len(pool))))


def main():
    print("Loading orders…")
    with open(INPUT, newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    by_inc = {r['Increment Id'].strip(): r for r in rows}
    print(f"  Input rows   : {len(rows):,}")

    cats = categorize(rows)
    rng = random.Random(SEED)

    selected = set()
    plan = [
        ('fx (conversion devise)', cats['fx'], 40),
        ('pending (paiement incomplet)', cats['pending'], 40),
        ('refunded', cats['refunded'], 40),
        ('not_full_shipped (Invoiced/Mixed — pas de Fulfillment Line)', cats['not_full_shipped'], 100),
        ('large (>=10 items)', cats['large'], 40),
        ('sendcloud (point relais → Note)', cats['sendcloud'], 40),
    ]
    for label, pool, n in plan:
        s = pick(rng, pool, n)
        selected |= s
        print(f"  {label}: {len(s)}/{len(pool)}")

    for pm in NON_MOLLIE_METHODS:
        pool = cats['by_payment'].get(pm, [])
        s = pick(rng, pool, 15)
        selected |= s
        print(f"  payment={pm}: {len(s)}/{len(pool)}")

    for pm in MOLLIE_METHODS:
        pool = cats['by_payment'].get(pm, [])
        s = pick(rng, pool, 10)
        selected |= s
        print(f"  payment={pm}: {len(s)}/{len(pool)}")

    for store, pool in cats['by_store'].items():
        s = pick(rng, pool, 15)
        selected |= s
        print(f"  store={store}: {len(s)}/{len(pool)}")

    if len(selected) < TARGET_MAX:
        remaining = [inc for inc in by_inc if inc not in selected]
        fill = pick(rng, remaining, TARGET_MAX - len(selected))
        selected |= fill
        print(f"  random fill: {len(fill)}")
    elif len(selected) > TARGET_MAX:
        selected = set(rng.sample(sorted(selected), TARGET_MAX))

    print(f"\n  Total sélectionné : {len(selected)} commandes")

    rows_by_store = {'dandoy': [], 'butterfly': []}
    for inc in selected:
        order = by_inc[inc]
        tag, out_rows = base.build_rows(order)
        if out_rows and tag in rows_by_store:
            rows_by_store[tag].extend(out_rows)

    outputs = {'dandoy': OUTPUT_DANDOY, 'butterfly': OUTPUT_BUTTERFLY}
    for store, all_rows in rows_by_store.items():
        with open(outputs[store], 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=base.SHOPIFY_COLS)
            writer.writeheader()
            writer.writerows(all_rows)
        n_orders = len(set(r['Name'] for r in all_rows if r.get('Name')))
        print(f"\n=== {store} ===")
        print(f"  Commandes   : {n_orders}")
        print(f"  Lignes CSV  : {len(all_rows):,}")
        print(f"  Écrit dans  : {outputs[store]}")


if __name__ == '__main__':
    main()
