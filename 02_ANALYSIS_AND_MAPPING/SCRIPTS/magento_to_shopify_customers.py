#!/usr/bin/env python3
"""
Magento customer + address CSV  →  Shopify customers CSV (Matrixify format)

Rules:
- Deduplicate by email (keep the most recent account if duplicates across websites)
- Merge default billing + shipping addresses
- Tag customers by source website (dandoy, butterfly)
- Passwords cannot be migrated (Shopify uses different hashing)
"""

import csv
from collections import defaultdict

INPUT_CUSTOMERS  = '/home/gregory/Documents/Labo/dandoy/01_DATA_RAW/export_customer.csv'
INPUT_ADDRESSES  = '/home/gregory/Documents/Labo/dandoy/01_DATA_RAW/export_customer_address.csv'
OUTPUT           = '/home/gregory/Documents/Labo/dandoy/04_SHOPIFY_IMPORTS/shopify_customers.csv'

SHOPIFY_COLS = [
    'Command',
    'First Name', 'Last Name', 'Email', 'Phone',
    'Accepts Email Marketing', 'Tags',
    'Tax Exempt', 'Tax Exemptions',
    'Address First Name', 'Address Last Name', 'Address Company',
    'Address1', 'Address2', 'Address City',
    'Address Province', 'Address Province Code',
    'Address Country', 'Address Country Code',
    'Address Zip', 'Address Phone',
    'Address Default',
]

WEBSITE_TAGS = {
    'base':  'dandoy',
    'ds_ww': 'dandoy',
    'bt_be': 'butterfly',
    'bt_nl': 'butterfly',
}


def main():
    # ------------------------------------------------------------------
    # Load customers
    # ------------------------------------------------------------------
    print("Loading customers…")
    with open(INPUT_CUSTOMERS, encoding='utf-8') as f:
        raw_customers = list(csv.DictReader(f))
    print(f"  Raw rows: {len(raw_customers)}")

    # Deduplicate by email: keep most recently updated, merge tags
    by_email = {}
    for c in raw_customers:
        email = c.get('email', '').lower().strip()
        if not email:
            continue

        website = c.get('_website', '')
        tag = WEBSITE_TAGS.get(website, website)

        if email in by_email:
            existing = by_email[email]
            existing['_tags'].add(tag)
            if c.get('updated_at', '') > existing.get('updated_at', ''):
                tags = existing['_tags']
                by_email[email] = c
                by_email[email]['_tags'] = tags
        else:
            c['_tags'] = {tag}
            by_email[email] = c

    print(f"  Unique emails: {len(by_email)}")

    # ------------------------------------------------------------------
    # Load addresses
    # ------------------------------------------------------------------
    print("Loading addresses…")
    with open(INPUT_ADDRESSES, encoding='utf-8') as f:
        raw_addresses = list(csv.DictReader(f))
    print(f"  Raw rows: {len(raw_addresses)}")

    # Index addresses by email
    # Priority: default billing first, then default shipping, then first found
    addr_by_email = defaultdict(list)
    for a in raw_addresses:
        email = a.get('_email', '').lower().strip()
        if email:
            addr_by_email[email].append(a)

    # ------------------------------------------------------------------
    # Write Shopify CSV
    # ------------------------------------------------------------------
    print("Writing Shopify CSV…")
    counters = {'customers': 0, 'with_address': 0, 'no_address': 0}

    with open(OUTPUT, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=SHOPIFY_COLS)
        writer.writeheader()

        for email, cust in by_email.items():
            tags = sorted(cust.get('_tags', set()))

            # Find best address: prefer default billing, then default shipping
            addresses = addr_by_email.get(email, [])
            best_addr = None
            for a in addresses:
                if a.get('_address_default_billing_') == '1':
                    best_addr = a
                    break
            if not best_addr:
                for a in addresses:
                    if a.get('_address_default_shipping_') == '1':
                        best_addr = a
                        break
            if not best_addr and addresses:
                best_addr = addresses[0]

            out = {col: '' for col in SHOPIFY_COLS}
            out['Command'] = 'MERGE'
            out['First Name'] = cust.get('firstname', '').strip()
            out['Last Name'] = cust.get('lastname', '').strip()
            out['Email'] = email
            out['Accepts Email Marketing'] = 'yes' if cust.get('is_review_booster_subscriber') == '1' else 'no'
            out['Tags'] = ','.join(tags)
            out['Tax Exempt'] = ''

            if best_addr:
                street = best_addr.get('street', '')
                lines = street.split('\n') if '\n' in street else [street]

                out['Address First Name'] = best_addr.get('firstname', '').strip()
                out['Address Last Name'] = best_addr.get('lastname', '').strip()
                out['Address Company'] = best_addr.get('company', '').strip()
                out['Address1'] = lines[0].strip() if lines else ''
                out['Address2'] = lines[1].strip() if len(lines) > 1 else ''
                out['Address City'] = best_addr.get('city', '').strip()
                out['Address Province'] = best_addr.get('region', '').strip()
                out['Address Country Code'] = best_addr.get('country_id', '').strip()
                out['Address Zip'] = best_addr.get('postcode', '').strip()
                out['Address Phone'] = best_addr.get('telephone', '').strip()
                out['Address Default'] = 'TRUE'
                counters['with_address'] += 1
            else:
                counters['no_address'] += 1

            # Phone from address if available
            if not out['Phone'] and best_addr:
                out['Phone'] = best_addr.get('telephone', '').strip()

            writer.writerow(out)
            counters['customers'] += 1

    print(f"\nDone.")
    print(f"  Customers exported : {counters['customers']}")
    print(f"  With address       : {counters['with_address']}")
    print(f"  Without address    : {counters['no_address']}")
    print(f"\nOutput → {OUTPUT}")
    print(f"\n⚠  Passwords cannot be migrated — customers will need to reset via 'Forgot password'.")


if __name__ == '__main__':
    main()
