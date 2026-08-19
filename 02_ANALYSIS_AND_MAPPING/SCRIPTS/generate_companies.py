#!/usr/bin/env python3
"""
Club discount mapping + Magento customers  →  Shopify B2B Companies CSV (Matrixify format)

Dandoy-Sports only. Butterfly is blocked (needs 4 Catalogs, Basic plan caps at 3 —
see 05_DOCS/mapping/club-b2b.md §2/§4).

One Company per club (group_id), one Location per Company, one Catalog assigned
(Dandoy — Club 20% / Dandoy — Club 15%, created manually in Shopify Admin — see
05_DOCS/mapping/club-b2b.md). All club members are linked as contacts with the
"Ordering only" role — no main contact and no address are set on import; the
client will complete both manually after migration (decision 19 August 2026).

Prerequisite: shopify_customers_dandoy.csv must be imported into Shopify before
this file, since Matrixify links contacts by email and fails the row otherwise.
"""

import csv
from collections import defaultdict

INPUT_MAPPING   = '/home/gregory/Documents/Labo/dandoy/02_ANALYSIS_AND_MAPPING/club_discount_mapping.csv'
INPUT_CUSTOMERS = '/home/gregory/Documents/Labo/dandoy/01_DATA_RAW/export_customer.csv'
OUTPUT_DANDOY   = '/home/gregory/Documents/Labo/dandoy/04_SHOPIFY_IMPORTS/shopify_companies_dandoy.csv'

# Same website → brand mapping as magento_to_shopify_customers.py, restricted to
# the Dandoy-tagged websites — a club member must exist in shopify_customers_dandoy.csv
# for the Customer: Email link to succeed on import.
DANDOY_WEBSITES = {'base', 'ds_ww'}

COMPANY_COLS = [
    'Name', 'Command', 'External ID', 'Notes', 'Customer Since',
    'Main Contact: Customer ID', 'Main Contact: Customer Email',
    'Location: Name', 'Location: Command', 'Location: External ID',
    'Location: Phone', 'Location: Notes', 'Location: Locale',
    'Location: Tax ID', 'Location: Tax Exemptions',
    'Location: Allow Shipping To Any Address', 'Location: Checkout To Draft',
    'Location: Checkout Payment Terms', 'Location: Catalogs',
    'Location: Shipping Recipient', 'Location: Shipping Phone',
    'Location: Shipping Address 1', 'Location: Shipping Address 2',
    'Location: Shipping Zip', 'Location: Shipping City',
    'Location: Shipping Province Code', 'Location: Shipping Country Code',
    'Location: Billing Recipient', 'Location: Billing Phone',
    'Location: Billing Address 1', 'Location: Billing Address 2',
    'Location: Billing Zip', 'Location: Billing City',
    'Location: Billing Province Code', 'Location: Billing Country Code',
    'Customer: Email', 'Customer: Command', 'Customer: Location Role',
]


def main():
    # ------------------------------------------------------------------
    # Load Dandoy club → catalog mapping
    # ------------------------------------------------------------------
    print("Loading club discount mapping…")
    with open(INPUT_MAPPING, encoding='utf-8') as f:
        mapping_rows = list(csv.DictReader(f))

    dandoy_clubs = [r for r in mapping_rows if r['brand'] == 'Dandoy']
    print(f"  Dandoy clubs: {len(dandoy_clubs)}")

    # ------------------------------------------------------------------
    # Load customers, index emails by group_id (Dandoy-side accounts only)
    # ------------------------------------------------------------------
    print("Loading customers…")
    with open(INPUT_CUSTOMERS, encoding='utf-8') as f:
        raw_customers = list(csv.DictReader(f))
    print(f"  Raw rows: {len(raw_customers)}")

    emails_by_group = defaultdict(list)
    for c in raw_customers:
        if c.get('_website') not in DANDOY_WEBSITES:
            continue
        email = c.get('email', '').lower().strip()
        group_id = c.get('group_id', '').strip()
        if email and group_id:
            emails_by_group[group_id].append(email)

    # ------------------------------------------------------------------
    # Write Shopify Companies CSV
    # ------------------------------------------------------------------
    print("Writing Companies CSV…")
    n_companies = 0
    n_contacts = 0
    n_empty_companies = 0

    with open(OUTPUT_DANDOY, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=COMPANY_COLS)
        w.writeheader()

        for club in dandoy_clubs:
            group_id = club['group_id']
            club_name = club['club_name'].strip()
            catalog_name = club['catalog_name']

            base = {col: '' for col in COMPANY_COLS}
            base['Name'] = club_name
            base['Command'] = 'MERGE'
            base['External ID'] = f'magento-club-{group_id}'
            base['Location: Name'] = club_name
            base['Location: Command'] = 'MERGE'
            base['Location: External ID'] = f'magento-club-{group_id}-loc1'
            base['Location: Catalogs'] = catalog_name
            base['Customer: Command'] = 'MERGE'
            base['Customer: Location Role'] = 'Ordering only'

            emails = sorted(set(emails_by_group.get(group_id, [])))
            n_companies += 1

            if not emails:
                # Still create the Company + Location even with no linked member found.
                w.writerow(base)
                n_empty_companies += 1
                continue

            for email in emails:
                row = dict(base)
                row['Customer: Email'] = email
                w.writerow(row)
                n_contacts += 1

    print("\nDone.")
    print(f"  Companies written : {n_companies}")
    print(f"  Contacts written  : {n_contacts}")
    if n_empty_companies:
        print(f"  ⚠ Companies with no matched Dandoy customer: {n_empty_companies}")
    print(f"\nOutput → {OUTPUT_DANDOY}")
    print("\n⚠ No address and no Main Contact set — client to complete manually after migration.")
    print("⚠ Import order: shopify_customers_dandoy.csv MUST be imported before this file.")


if __name__ == '__main__':
    main()
