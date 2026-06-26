#!/usr/bin/env python3
"""
Magento orders CSV (wide format)  →  Shopify orders CSV (Matrixify format)

Source  : order-all-2025-2026.csv
          - 1 row per order, items in columns: item 1(Sku), item 2(Sku)…
          - Line items with SKU, name, price, qty, status, taxes, discounts
          - No billing/shipping address details (only firstname/lastname)

Output  : shopify_orders.csv
          - 1 row per line item (Matrixify "long" format)
          - Order header fields repeated on first row only

Matrixify import: Import → Orders sheet
"""

import csv
import sys
from datetime import datetime

INPUT  = '/home/gregory/Documents/Labo/dandoy/01_DATA_RAW/export_order_all_2025_2026.csv'
OUTPUT = '/home/gregory/Documents/Labo/dandoy/04_SHOPIFY_IMPORTS/shopify_orders.csv'

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

SHOPIFY_COLS = [
    'Name',
    'Email',
    'Financial Status',
    'Fulfillment Status',
    'Currency',
    'Subtotal',
    'Shipping',
    'Taxes',
    'Total',
    'Lineitem name',
    'Lineitem quantity',
    'Lineitem price',
    'Lineitem sku',
    'Lineitem requires shipping',
    'Lineitem taxable',
    'Lineitem fulfillment status',
    'Lineitem discount',
    'Billing Name',
    'Billing Address1',
    'Billing Address2',
    'Billing City',
    'Billing Province',
    'Billing Zip',
    'Billing Country',
    'Billing Phone',
    'Shipping Name',
    'Shipping Address1',
    'Shipping Address2',
    'Shipping City',
    'Shipping Province',
    'Shipping Zip',
    'Shipping Country',
    'Shipping Phone',
    'Shipping Line Title',
    'Shipping Line Price',
    'Payment Method',
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


def fulfillment_status(statuses):
    """List of item statuses → order fulfillment status."""
    if not statuses:
        return 'unfulfilled'
    shipped = sum(1 for s in statuses if s.lower() in ('shipped', 'complete', 'invoiced'))
    if shipped == len(statuses):
        return 'fulfilled'
    if shipped > 0:
        return 'partial'
    return 'unfulfilled'


def item_fulfillment(status):
    return 'fulfilled' if status.lower() in ('shipped', 'complete', 'invoiced') else 'unfulfilled'


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
        return []

    item_statuses = [it['status'] for it in items]
    order_name    = order['Increment Id'].strip()
    payment       = PAYMENT_MAP.get(order.get('Payment Method', '').strip(),
                                    order.get('Payment Method', '').strip())
    tag           = store_tag(order.get('Store Name', ''))
    fin_status    = financial_status(order)
    ful_status    = fulfillment_status(item_statuses)
    b_name        = billing_name(order)
    s_name        = shipping_name(order)
    created       = parse_date(order.get('Created At', ''))

    # Compute taxes from items (approximate: price × qty × tax_rate)
    taxes = sum(it['price'] * it['qty'] * (it['tax_pct'] / 100) for it in items)

    rows = []
    for idx, item in enumerate(items):
        taxable = 'TRUE' if item['tax_pct'] > 0 else 'FALSE'
        r = {col: '' for col in SHOPIFY_COLS}

        # Line item fields (every row)
        r['Lineitem name']               = item['name']
        r['Lineitem quantity']           = item['qty']
        r['Lineitem price']              = f"{item['price']:.4f}"
        r['Lineitem sku']                = item['sku']
        r['Lineitem requires shipping']  = 'TRUE'
        r['Lineitem taxable']            = taxable
        r['Lineitem fulfillment status'] = item_fulfillment(item['status'])
        r['Lineitem discount']           = f"{item['discount']:.4f}" if item['discount'] else ''

        # Order header fields (first row only)
        if idx == 0:
            r['Name']               = order_name
            r['Email']              = order.get('Customer Email', '').strip().lower()
            r['Financial Status']   = fin_status
            r['Fulfillment Status'] = ful_status
            r['Currency']           = 'EUR'
            r['Subtotal']           = order.get('Subtotal', '').strip()
            r['Shipping']           = order.get('Base Shipping Incl Tax', '').strip()
            r['Taxes']              = f"{taxes:.2f}"
            r['Total']              = order.get('Grand Total', '').strip()
            r['Billing Name']       = b_name
            r['Shipping Name']      = s_name
            r['Shipping Line Title']= order.get('Shipping Description', '').strip()
            r['Shipping Line Price']= order.get('Base Shipping Incl Tax', '').strip()
            r['Payment Method']     = payment
            r['Tags']               = tag
            r['Created at']         = created
        else:
            # Repeat Name to link this row to the order
            r['Name'] = order_name

        rows.append(r)

    return rows


def main():
    print("Loading orders…")
    with open(INPUT, newline='', encoding='utf-8') as f:
        orders = list(csv.DictReader(f))
    print(f"  Input rows   : {len(orders):,}")

    all_rows = []
    skipped  = 0
    for order in orders:
        rows = build_rows(order)
        if rows:
            all_rows.extend(rows)
        else:
            skipped += 1

    print(f"  Output rows  : {len(all_rows):,}")
    print(f"  Skipped      : {skipped} (no items)")

    with open(OUTPUT, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=SHOPIFY_COLS)
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"  Written to   : {OUTPUT}")

    # Quick stats
    orders_written = sum(1 for r in all_rows if r.get('Email'))
    print(f"\nStats :")
    print(f"  Commandes avec items : {orders_written:,}")
    fin_counts = {}
    for r in all_rows:
        s = r.get('Financial Status')
        if s:
            fin_counts[s] = fin_counts.get(s, 0) + 1
    for s, c in sorted(fin_counts.items()):
        print(f"  Financial status [{s}] : {c:,}")


if __name__ == '__main__':
    main()
