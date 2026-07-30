#!/usr/bin/env python3
"""
Magento orders CSV (wide format)  →  Shopify orders CSV (Matrixify format)

Source  : order-all-2025-2026.csv
          - 1 row per order, items in columns: item 1(Sku), item 2(Sku)…
          - Line items with SKU, name, price, qty, status, taxes, discounts
          - Billing/Shipping address: Firstname, Lastname, Street, City, Region,
            Postcode, Country Id (ISO code), Telephone, Company

Output  : shopify_orders_dandoy.csv / shopify_orders_butterfly.csv
          - 1 row per line item (Matrixify "long" format)
          - Order header fields repeated on first row only

Two Shopify stores (Option B): each order was placed on exactly one
Magento website (Store Name), so it is written to exactly one store's
file — no duplication needed here, unlike products/customers.

Matrixify import: Import → Orders sheet
"""

import csv
import sys
from datetime import datetime
from itertools import count

# Line: ID must be a unique number per line item row (Matrixify requirement,
# not per-order) — a single counter shared across every order keeps that
# true regardless of how orders get split across the two store output files.
_line_id_counter = count(1)

INPUT            = '/home/gregory/Documents/Labo/dandoy/01_DATA_RAW/export_order_all_2025_2026.csv'
OUTPUT_DANDOY    = '/home/gregory/Documents/Labo/dandoy/04_SHOPIFY_IMPORTS/shopify_orders_dandoy.csv'
OUTPUT_BUTTERFLY = '/home/gregory/Documents/Labo/dandoy/04_SHOPIFY_IMPORTS/shopify_orders_butterfly.csv'

MAX_ITEMS = 56

PAYMENT_MAP = {
    'mollie_methods_creditcard':    'Credit Card',
    'mollie_methods_paypal':        'PayPal',
    'mollie_methods_bancontact':    'Bancontact',
    'mollie_methods_ideal':         'iDEAL',
    'mollie_methods_klarna':        'Klarna',
    'mollie_methods_klarnapaylater':'Klarna Pay Later',
    'payplug_payments_standard':    'Credit Card',
    'payplug_payments_ideal':       'iDEAL',
    'payplug_payments_bancontact':  'Bancontact',
    'paypal_express':               'PayPal',
    'free':                         'Free',
}

STORE_TAGS = {
    'dandoy sports eu': 'dandoy',
    'dandoy sports ww': 'dandoy',
    'butterfly be':     'butterfly',
    'butterfly nl':     'butterfly',
}

# Column names below mix two Matrixify conventions on purpose:
# - Plain names (Billing Name, Billing City…) are the ones confirmed working
#   against a live Matrixify import test (2026-07-30).
# - "Section: Field" names (Payment: Status, Line: Name, Billing: Address 1…)
#   are Matrixify's current documented convention — required for the fields
#   that a live test proved fail silently as "unknown column" under their
#   old plain-name equivalent (Financial Status, Lineitem name, Subtotal,
#   Shipping, Taxes, Total, Billing/Shipping Address1/2, Payment Method).
# Don't rename the plain ones back to colon form without testing — some
# colon fields (e.g. Billing: Name) may not carry the same alias.
#
# 'Line: Type' + 'Line: ID' are mandatory for a row to be recognized as a
# line item at all — without them Matrixify rejected every order with
# "must have at least one line item" despite Quantity/Price/SKU being
# present (confirmed via a second live test, 2026-07-30). 'Line: Title'
# is the field Shopify actually displays; 'Line: Name' is accepted but
# silently ignored by Shopify on import (kept anyway, harmless).
#
# No 'Line: Fulfillment Status' / 'Fulfillment Status' column at all: both
# are export-only (computed from actual Fulfillment records, not settable)
# — writing either made Matrixify validate our value against the unrelated
# Fulfillment-record status enum (cancelled/error/failure/open/pending/
# success) and reject every row (confirmed via 2 live tests, 2026-07-30).
# To reflect real fulfillment status on import, Matrixify requires extra
# 'Line: Type' = 'Fulfillment Line' rows per shipped order (Fulfillment: ID,
# Fulfillment: Status, matching Line: Title/Variant Title/Price/Quantity) —
# out of scope for now; all imported orders will show as unfulfilled until
# that's implemented.
SHOPIFY_COLS = [
    'Name',
    'Command',
    'Email',
    'Payment: Status',
    'Currency',
    'Price: Subtotal',
    'Price: Current Total Shipping',
    'Tax: Total',
    'Price: Total',
    'Line: Type',
    'Line: ID',
    'Line: Title',
    'Line: Name',
    'Line: Quantity',
    'Line: Price',
    'Line: SKU',
    'Line: Requires Shipping',
    'Line: Taxable',
    'Line: Discount',
    'Billing Name',
    'Billing: Address 1',
    'Billing: Address 2',
    'Billing City',
    'Billing Province',
    'Billing Zip',
    'Billing Country',
    'Billing Phone',
    'Shipping Name',
    'Shipping: Address 1',
    'Shipping: Address 2',
    'Shipping City',
    'Shipping Province',
    'Shipping Zip',
    'Shipping Country',
    'Shipping Phone',
    'Shipping Line Title',
    'Shipping Line Price',
    'Transaction: Payment Method',
    'Tags',
    'Note',
    'Created at',
]


def parse_date(raw):
    """Jan 1, 2025 02:12:20 AM  →  2025-01-01 02:12:20 +0100"""
    try:
        dt = datetime.strptime(raw.strip(), '%b %d, %Y %I:%M:%S %p')
        return dt.strftime('%Y-%m-%d %H:%M:%S +0100')
    except ValueError:
        return raw.strip()


def parse_float(raw):
    try:
        return float((raw or '').replace(',', '').strip())
    except ValueError:
        return 0.0


def financial_status(row):
    due   = parse_float(row.get('Total Due'))
    paid  = parse_float(row.get('Total Paid'))
    refunded = parse_float(row.get('Subtotal Refunded'))
    if refunded > 0:
        return 'refunded'
    if due > 0:
        return 'pending'
    if paid > 0:
        return 'paid'
    return 'paid'


def store_tag(store_name):
    name_lower = store_name.lower()
    for key, tag in STORE_TAGS.items():
        if key in name_lower:
            return tag
    return 'dandoy'


def billing_name(row):
    first = row.get('BillingAddress.Firstname', '').strip()
    last  = row.get('BillingAddress.Lastname', '').strip()
    return f"{first} {last}".strip() or f"{row.get('Customer Firstname','').strip()} {row.get('Customer Lastname','').strip()}".strip()


def shipping_name(row):
    first = row.get('ShippingAddress.Firstname', '').strip()
    last  = row.get('ShippingAddress.Lastname', '').strip()
    return f"{first} {last}".strip() or billing_name(row)


# Magento's multi-line street attribute is exported tab-separated, and a
# significant share of rows duplicate the city on its own line (or as
# "postcode city" glued together) — including it verbatim would show the
# city twice in the Shopify address. Drop any line that is the city itself
# or ends with it (postcode+city case) before recombining the rest.
def clean_street(street, city):
    city = (city or '').strip()
    city_l = city.lower()
    parts = [p.strip() for p in (street or '').split('\t') if p.strip()]
    if city_l:
        parts = [p for p in parts
                  if p.lower() != city_l
                  and not (len(p) > len(city_l) and p.lower().endswith(city_l))]
    return ', '.join(parts)


def address_fields(row, prefix):
    """prefix: 'BillingAddress' or 'ShippingAddress'.

    Country is filled with the raw ISO code into Matrixify's 'Country'
    column (not a separate 'Country Code' column — that name isn't part of
    the Orders template and gets silently ignored, leaving 'Country' empty
    and the whole address rejected as invalid even though every other
    field is present)."""
    city = row.get(f'{prefix}.City', '').strip()
    return {
        'Address1': clean_street(row.get(f'{prefix}.Street', ''), city),
        'City':     city,
        'Province': row.get(f'{prefix}.Region', '').strip(),
        'Zip':      row.get(f'{prefix}.Postcode', '').strip(),
        'Country':  row.get(f'{prefix}.Country Id', '').strip(),
        'Phone':    row.get(f'{prefix}.Telephone', '').strip(),
    }


def extract_items(row):
    items = []
    for i in range(1, MAX_ITEMS + 1):
        sku = (row.get(f'item {i}(Sku)') or '').strip()
        if not sku:
            break
        items.append({
            'name':     (row.get(f'item {i}(Name)') or '').strip(),
            'sku':      sku,
            'price':    parse_float(row.get(f'item {i}(Price)')),
            'qty':      int(parse_float(row.get(f'item {i}(Qty Ordered)'))),
            'status':   (row.get(f'item {i}(Status)') or '').strip(),
            'tax_pct':  parse_float(row.get(f'item {i}(Tax Percent)')),
            'discount': parse_float(row.get(f'item {i}(Discount Amount)')),
        })
    return items


def build_rows(order):
    items = extract_items(order)
    if not items:
        return None, []

    order_name    = order['Increment Id'].strip()
    payment       = PAYMENT_MAP.get(order.get('Payment Method', '').strip(),
                                    order.get('Payment Method', '').strip())
    tag           = store_tag(order.get('Store Name', ''))
    fin_status    = financial_status(order)
    b_name        = billing_name(order)
    s_name        = shipping_name(order)
    b_addr        = address_fields(order, 'BillingAddress')
    s_addr        = address_fields(order, 'ShippingAddress')
    if not s_addr['Address1'] or not s_addr['City']:
        s_addr = b_addr
    created       = parse_date(order.get('Created At', ''))

    # Compute taxes from items (approximate: price × qty × tax_rate)
    taxes = sum(it['price'] * it['qty'] * (it['tax_pct'] / 100) for it in items)

    rows = []
    for idx, item in enumerate(items):
        taxable = 'TRUE' if item['tax_pct'] > 0 else 'FALSE'
        r = {col: '' for col in SHOPIFY_COLS}

        # Line item fields (every row)
        r['Line: Type']                = 'Line Item'
        r['Line: ID']                  = str(next(_line_id_counter))
        r['Line: Title']              = item['name']
        r['Line: Name']               = item['name']
        r['Line: Quantity']           = item['qty']
        r['Line: Price']              = f"{item['price']:.4f}"
        r['Line: SKU']                = item['sku']
        r['Line: Requires Shipping']  = 'TRUE'
        r['Line: Taxable']            = taxable
        r['Line: Discount']           = f"{item['discount']:.4f}" if item['discount'] else ''

        # Order header fields (first row only)
        if idx == 0:
            r['Name']               = order_name
            r['Command']            = 'MERGE'
            r['Email']              = order.get('Customer Email', '').strip().lower()
            r['Payment: Status']    = fin_status
            r['Currency']           = 'EUR'
            r['Price: Subtotal']    = order.get('Subtotal', '').strip()
            r['Price: Current Total Shipping'] = order.get('Base Shipping Incl Tax', '').strip()
            r['Tax: Total']         = f"{taxes:.2f}"
            r['Price: Total']       = order.get('Grand Total', '').strip()
            r['Billing Name']       = b_name
            r['Billing: Address 1'] = b_addr['Address1']
            r['Billing City']       = b_addr['City']
            r['Billing Province']   = b_addr['Province']
            r['Billing Zip']        = b_addr['Zip']
            r['Billing Country']    = b_addr['Country']
            r['Billing Phone']      = b_addr['Phone']
            r['Shipping Name']      = s_name
            r['Shipping: Address 1'] = s_addr['Address1']
            r['Shipping City']      = s_addr['City']
            r['Shipping Province']  = s_addr['Province']
            r['Shipping Zip']       = s_addr['Zip']
            r['Shipping Country']   = s_addr['Country']
            r['Shipping Phone']     = s_addr['Phone']
            r['Shipping Line Title']= order.get('Shipping Description', '').strip()
            r['Shipping Line Price']= order.get('Base Shipping Incl Tax', '').strip()
            r['Transaction: Payment Method'] = payment
            r['Tags']               = tag
            r['Created at']         = created
        else:
            # Repeat Name to link this row to the order
            r['Name'] = order_name

        rows.append(r)

    return tag, rows


def main():
    print("Loading orders…")
    with open(INPUT, newline='', encoding='utf-8') as f:
        orders = list(csv.DictReader(f))
    print(f"  Input rows   : {len(orders):,}")

    rows_by_store = {'dandoy': [], 'butterfly': []}
    skipped  = 0
    for order in orders:
        tag, rows = build_rows(order)
        if rows and tag in rows_by_store:
            rows_by_store[tag].extend(rows)
        else:
            skipped += 1

    outputs = {'dandoy': OUTPUT_DANDOY, 'butterfly': OUTPUT_BUTTERFLY}
    print(f"  Skipped      : {skipped} (no items / unknown store)")

    for store, all_rows in rows_by_store.items():
        with open(outputs[store], 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=SHOPIFY_COLS)
            writer.writeheader()
            writer.writerows(all_rows)

        orders_written = sum(1 for r in all_rows if r.get('Email'))
        print(f"\n=== {store} ===")
        print(f"  Output rows           : {len(all_rows):,}")
        print(f"  Commandes avec items  : {orders_written:,}")
        fin_counts = {}
        for r in all_rows:
            s = r.get('Payment: Status')
            if s:
                fin_counts[s] = fin_counts.get(s, 0) + 1
        for s, c in sorted(fin_counts.items()):
            print(f"  Payment status [{s}] : {c:,}")
        print(f"  Written to            : {outputs[store]}")


if __name__ == '__main__':
    main()
