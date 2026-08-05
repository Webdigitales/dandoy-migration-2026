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

# Gift cards (product_type = mageworx_giftcards in the catalogue export)
# never carry Shipped — there's no physical parcel, so Magento leaves them
# at Invoiced forever. 216/329 "not fully shipped" orders are 100% gift
# cards (client-confirmed 2026-08-05), plus 5 more mix a Shipped physical
# item with an Invoiced gift card line — both cases should count as fully
# fulfilled for the 'all items shipped' check below.
GIFT_CARD_SKUS = {'giftcard-25', 'giftcard-50', 'giftcard-75', 'giftcard-100'}

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
#
# Fulfillment status IS settable, but only via an extra row per order with
# 'Line: Type' = 'Fulfillment Line' and 'Line: ID' left EMPTY (a filled-in
# ID makes Matrixify treat it as a partial fulfillment referencing that
# Line Item ID — confirmed live, 2026-08-04: all 5 sample orders failed
# with "Cannot find Line Item [N] to fulfill" until Line: ID was dropped).
# 99.2% of orders (38,722/39,051) have every item at Status='Shipped', so
# one full-order Fulfillment Line row is enough for those; the remaining
# 0.8% (Invoiced/Mixed item statuses) are left unfulfilled rather than
# guess a wrong state. 'Fulfillment: Processed At' (the historical ship
# date) is mapped from Magento's 'Updated At' (added to the export
# 2026-08-04) — an approximation (last order modification, not a true
# ship date), but the only field covering 100% of orders; bpost-only
# fields cover just 18% by carrier and were dropped as a candidate.
#
# 'Tax: Total' alone is NOT enough to make tax show up in the order total:
# per Matrixify's own docs, "if any Line Item ... has tax applied in the
# import file, then order level tax will not be imported to avoid
# duplicating taxes" — and without a per-line tax entry, no tax gets
# applied at all. Confirmed live: order WEB1-0125-17658 showed Total =
# Subtotal - Discount with the 18.82€ VAT entirely missing. Fixed via
# 'Line: Tax 1 Title/Rate/Price' per item instead.
SHOPIFY_COLS = [
    'Name',
    'Command',
    'Email',
    'Payment: Status',
    'Currency',
    'Price: Subtotal',
    'Price: Current Total Shipping',
    'Tax: Total',
    'Price: Total Discount',
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
    'Line: Tax 1 Title',
    'Line: Tax 1 Rate',
    'Line: Tax 1 Price',
    'Line: Discount',
    'Fulfillment: Status',
    'Fulfillment: Shipment Status',
    'Fulfillment: Processed At',
    'Fulfillment: Send Receipt',
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


DATE_FORMATS = (
    '%b %d, %Y %I:%M:%S %p',  # Created At: 'Jan 1, 2025 02:12:20 AM'
    '%Y-%m-%d %H:%M:%S',      # Updated At: '2025-01-02 11:11:43'
)


def parse_date(raw):
    """→ 2025-01-01 02:12:20 +0100 (either source format above)."""
    raw = raw.strip()
    for fmt in DATE_FORMATS:
        try:
            dt = datetime.strptime(raw, fmt)
            return dt.strftime('%Y-%m-%d %H:%M:%S +0100')
        except ValueError:
            continue
    return raw


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


# Client's own diagnostic rule (confirmed 2026-08-05): a physical order
# invoiced but never shipped means the customer cancelled and was
# refunded — Magento's export carries no explicit refund flag for these
# (Subtotal Refunded stays empty, Total Paid = Grand Total), so this
# status pattern IS the signal. Doesn't apply to gift cards, which never
# reach 'Shipped' by nature and are handled separately (GIFT_CARD_SKUS).
def is_unshipped_refund(items):
    return bool(items) and all(
        it['status'] == 'Invoiced' and it['sku'] not in GIFT_CARD_SKUS
        for it in items
    )


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
# significant share of rows duplicate the city — either as its own line, or
# glued onto the end of a line ("26 rue du bois 60570 ANDEVILLE" followed by
# a second line "ANDEVILLE", or a single line "Terwenstraat 5, Gouda" with
# no second line at all). Including it verbatim would show the city twice
# in the Shopify address.
#
# Each line is handled independently rather than by line count: a line
# that IS the city gets dropped outright (genuine duplicate); a line that
# merely ENDS WITH the city gets the city suffix trimmed off, keeping the
# rest of the line. An earlier version dropped any line ending with the
# city wholesale, which silently emptied Address 1 whenever that was the
# ONLY line carrying real street data — confirmed live via two rounds of
# testing (2026-08-04): 8/950 orders in the stratified sample failed
# Matrixify's address validation outright, and a full-dataset scan then
# found 45 more (out of 58 total empty-despite-source-data cases; the
# remaining 13 are genuinely empty in Magento — street equals city with no
# separate address at all, nothing to recover).
def clean_street(street, city):
    city = (city or '').strip()
    city_l = city.lower()
    raw_parts = [p.strip() for p in (street or '').split('\t') if p.strip()]
    parts = []
    for p in raw_parts:
        if city_l and p.lower() == city_l:
            continue
        if city_l and len(p) > len(city_l) and p.lower().endswith(city_l):
            p = p[:-len(city_l)].rstrip(' ,\t-')
        if p:
            parts.append(p)
    # Drop consecutive duplicates left behind by the trimming above (e.g. a
    # postcode-only line matching the postcode already at the end of the
    # previous line).
    deduped = []
    for p in parts:
        if not deduped or deduped[-1].lower() != p.lower():
            deduped.append(p)
    return ', '.join(deduped)


# Relay point columns for 3 possible carriers (bpost/DPD/Sendcloud), tried
# in this order — in practice only Sendcloud is ever populated (23.8% of
# orders, confirmed 2026-08-04); bpost/DPD columns exist in the export but
# were empty in every order checked, kept as a harmless fallback in case
# that changes.
RELAY_POINT_FIELDS = (
    ('Bpost Point Office', 'Bpost Point Street', 'Bpost Point Nr',
     'Bpost Point Zip', 'Bpost Point City'),
    ('Dpd Parcelshop Name', 'Dpd Parcelshop Street', 'Dpd Parcelshop House Number',
     'Dpd Parcelshop Zip Code', 'Dpd Parcelshop City'),
    ('Sendcloud Service Point Name', 'Sendcloud Service Point Street',
     'Sendcloud Service Point House Number', 'Sendcloud Service Point Zip Code',
     'Sendcloud Service Point City'),
)


def order_note(row):
    """'Point relais: <name> <street> <nr>, <zip> <city> | Mollie: <id>'
    — either half omitted if not present on this order."""
    parts = []
    for name_col, street_col, nr_col, zip_col, city_col in RELAY_POINT_FIELDS:
        name = (row.get(name_col) or '').strip()
        if name:
            street = (row.get(street_col) or '').strip()
            nr     = (row.get(nr_col) or '').strip()
            zipc   = (row.get(zip_col) or '').strip()
            city   = (row.get(city_col) or '').strip()
            addr = ' '.join(p for p in (street, nr) if p)
            addr = ', '.join(p for p in (addr, f"{zipc} {city}".strip()) if p)
            parts.append(f"Point relais: {name} {addr}".strip())
            break

    mollie_id = (row.get('Mollie Transaction Id') or '').strip()
    if mollie_id:
        parts.append(f"Mollie: {mollie_id}")

    return ' | '.join(parts)


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


def fx_rate(row):
    """Some orders (997 of 39,051, all on the WW / non-EU store) have a
    'Grand Total' in the customer's local checkout currency alongside a
    'Base Grand_total' in EUR (the shop's base currency) — no explicit
    currency code is exported, only these two amounts. Everything else
    (Subtotal, item Price, Tax Amount, Discount Amount) is only given in
    the local currency, so we derive one conversion rate per order and
    apply it everywhere rather than mixing EUR and local-currency fields
    under a hardcoded Currency=EUR (confirmed bug: order WEB4-0125-22963
    was sent to Shopify as "112.38 EUR" when the real EUR amount is
    104.06€). Orders without this split (the other 97.5%) get rate=1.0,
    a no-op."""
    grand = parse_float(row.get('Grand Total'))
    base = parse_float(row.get('Base Grand_total'))
    if grand and base and abs(grand - base) > 0.01:
        return grand / base
    return 1.0


def extract_items(row, rate):
    items = []
    for i in range(1, MAX_ITEMS + 1):
        sku = (row.get(f'item {i}(Sku)') or '').strip()
        if not sku:
            break
        items.append({
            'name':     (row.get(f'item {i}(Name)') or '').strip(),
            'sku':      sku,
            'price':    parse_float(row.get(f'item {i}(Price)')) / rate,
            'qty':      int(parse_float(row.get(f'item {i}(Qty Ordered)'))),
            'status':   (row.get(f'item {i}(Status)') or '').strip(),
            'tax_pct':  parse_float(row.get(f'item {i}(Tax Percent)')),
            'tax_amt':  parse_float(row.get(f'item {i}(Tax Amount)')) / rate,
            'discount': parse_float(row.get(f'item {i}(Discount Amount)')) / rate,
        })
    return items


def build_rows(order):
    rate  = fx_rate(order)
    items = extract_items(order, rate)
    if not items:
        return None, []

    order_name    = order['Increment Id'].strip()
    payment       = PAYMENT_MAP.get(order.get('Payment Method', '').strip(),
                                    order.get('Payment Method', '').strip())
    tag           = store_tag(order.get('Store Name', ''))
    fin_status    = 'refunded' if is_unshipped_refund(items) else financial_status(order)
    b_name        = billing_name(order)
    s_name        = shipping_name(order)
    b_addr        = address_fields(order, 'BillingAddress')
    s_addr        = address_fields(order, 'ShippingAddress')
    if not s_addr['Address1'] or not s_addr['City']:
        s_addr = b_addr
    created       = parse_date(order.get('Created At', ''))

    # Use Magento's own per-item tax amounts rather than recomputing
    # price × qty × rate — that approximation ignores per-item discounts
    # entirely and overstates tax whenever a discount applies (confirmed:
    # order WEB1-0125-17658 computed 20.92 vs Magento's actual 18.82,
    # since the discount reduces the taxable base before Magento's own
    # calculation). Magento already did that math correctly.
    taxes = sum(it['tax_amt'] for it in items)

    # Magento's 'Discount Amount' is a tax-inclusive (TTC) figure, but
    # 'Line: Price' is tax-exclusive (HT, matches 'item N(Price)'/'Row
    # Total'). Sending the raw TTC discount next to an HT price makes
    # Shopify's own Total = Subtotal - Discount + Tax land 2-3% short of
    # Magento's real Grand Total (confirmed: order WEB1-0125-17658 —
    # Shopify computed 106.37€ vs the real 108.45€). Converting each
    # discount to its HT equivalent before subtracting fixes it exactly:
    # 99.59 - (12.05 / 1.21) + 18.82 = 108.45, matching Magento to the cent.
    for it in items:
        it['discount_ht'] = it['discount'] / (1 + it['tax_pct'] / 100) if it['tax_pct'] else it['discount']
    total_discount = sum(it['discount_ht'] for it in items)

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
        if item['tax_pct'] > 0:
            r['Line: Tax 1 Title'] = 'VAT'
            r['Line: Tax 1 Rate']  = f"{item['tax_pct'] / 100:.4f}"
            r['Line: Tax 1 Price'] = f"{item['tax_amt']:.4f}"
        r['Line: Discount']           = f"{item['discount_ht']:.4f}" if item['discount'] else ''

        # Order header fields (first row only)
        if idx == 0:
            r['Name']               = order_name
            r['Command']            = 'MERGE'
            r['Email']              = order.get('Customer Email', '').strip().lower()
            r['Payment: Status']    = fin_status
            r['Currency']           = 'EUR'
            r['Price: Subtotal']    = f"{parse_float(order.get('Subtotal')) / rate:.4f}"
            r['Price: Current Total Shipping'] = order.get('Base Shipping Incl Tax', '').strip()
            r['Tax: Total']         = f"{taxes:.2f}"
            r['Price: Total Discount'] = f"{total_discount:.2f}" if total_discount else ''
            # 'Base Grand_total' is already EUR — more direct and exact than
            # dividing 'Grand Total' by the same derived rate a second time.
            r['Price: Total']       = order.get('Base Grand_total', '').strip() or order.get('Grand Total', '').strip()
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
            r['Note']                = order_note(order)
            r['Created at']         = created
        else:
            # Repeat Name to link this row to the order
            r['Name'] = order_name

        rows.append(r)

    # Fulfillment Line: one full-order row when every item is either
    # 'Shipped' or a gift card (see GIFT_CARD_SKUS above — those never
    # reach 'Shipped'). 'Line: ID' must stay EMPTY here — confirmed via
    # a live Matrixify test (2026-08-04, all 5 sample orders failed):
    # setting it to a fresh unique ID made Matrixify treat the row as a
    # PARTIAL fulfillment referencing that specific Line Item ID, which
    # doesn't exist ("Error saving Fulfillment: Cannot find Line Item [8]
    # to fulfill" — 8 was this row's own made-up Line: ID). Leaving it
    # blank is what actually triggers "fulfill the whole order".
    if all(it['status'] == 'Shipped' or it['sku'] in GIFT_CARD_SKUS for it in items):
        f = {col: '' for col in SHOPIFY_COLS}
        f['Name']                      = order_name
        f['Command']                   = 'MERGE'
        f['Line: Type']                = 'Fulfillment Line'
        f['Fulfillment: Status']       = 'success'
        # Matrixify requires 'Shipment Status' whenever 'Processed At' is
        # set ("you also need to set the 'Fulfillment: Shipment Status' of
        # 'delivered' or 'failure'" — confirmed live, 2026-08-04). These
        # are historical Shipped orders, so 'delivered' is the correct value.
        f['Fulfillment: Shipment Status'] = 'delivered'
        f['Fulfillment: Processed At'] = parse_date(order['Updated At']) if order.get('Updated At', '').strip() else ''
        f['Fulfillment: Send Receipt'] = 'FALSE'
        rows.append(f)

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
