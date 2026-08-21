#!/usr/bin/env python3
"""
Magento customer + address CSV  →  Shopify customers CSV (Matrixify format)

Rules:
- Deduplicate by email (keep the most recent account if duplicates across websites)
- Merge default billing + shipping addresses
- Tag customers by source website (dandoy, butterfly)
- Passwords cannot be migrated (Shopify uses different hashing)

Two Shopify stores (Option B): a customer is written to whichever store(s)
their tags cover — customers who registered on both brands (tagged
'dandoy' AND 'butterfly') are written into both stores' CSVs.
"""

import argparse
import csv
import re
from collections import defaultdict

import phonenumbers

INPUT_CUSTOMERS  = '/home/gregory/Documents/Labo/dandoy/01_DATA_RAW/export_customer.csv'
INPUT_ADDRESSES  = '/home/gregory/Documents/Labo/dandoy/01_DATA_RAW/export_customer_address.csv'
OUTPUT_DANDOY    = '/home/gregory/Documents/Labo/dandoy/04_SHOPIFY_IMPORTS/shopify_customers_dandoy.csv'
OUTPUT_BUTTERFLY = '/home/gregory/Documents/Labo/dandoy/04_SHOPIFY_IMPORTS/shopify_customers_butterfly.csv'

# Not in Shopify's list of sellable/shippable countries: either obsolete/
# uninhabited ISO territories, or (PR/GU/AS) US territories that Shopify
# represents as a US state rather than a top-level country — confirmed by
# the client's Matrixify import report ('"Address: Country Code" is not
# valid'). Addresses in these countries are dropped rather than sent to
# Matrixify with a Country Code it will reject outright.
UNSUPPORTED_COUNTRIES = {'AN', 'AQ', 'BV', 'GS', 'HM', 'PN', 'TF', 'UM', 'EH', 'PR', 'GU', 'AS'}

# Shopify's province/state list only reliably matched Magento's free-text
# 'region' for US addresses across two live Matrixify import rounds —
# BE/NL/LU have no province list at all, and even countries that DO have
# one (Romania, Japan, Canada, Mexico, Peru...) failed on spelling/
# diacritics mismatches Magento's export doesn't normalize ('Bucureşti',
# 'Aiti' for Aichi, 'Yukon Territory' instead of 'Yukon', 'Distrito
# Federal' instead of 'Ciudad de México'...). Without Shopify's canonical
# per-country subdivision list to match against, sending Province for any
# country outside this set is a coin flip on the next import — so it's
# just dropped (customer/order still import fine without it).
PROVINCE_SAFE_COUNTRIES = {'US'}

# Matrixify rejects First/Last Name containing links or markup outright
# ('First name cannot contain URL' etc.) — these are bot signups (spam
# 'investment opportunity' text dropped straight into the name fields on
# the old Magento site), not real customers, so the whole row is skipped
# rather than just blanking the name.
SPAM_NAME_RE = re.compile(r'https?://|www\.|<[a-z]+[ >/]', re.I)


def clean_phone(raw, country_id):
    """Normalize a Magento free-text phone into E.164 via phonenumbers
    (libphonenumber), or '' if it isn't a real, dialable number — Matrixify
    rejects the row outright on 'Phone is invalid' rather than just dropping
    the field, so a best-effort guess is worse than leaving it blank. A
    syntactically plausible '+'-prefixed regex match isn't enough: real
    validation catches things like a bad area code or a double-prefixed
    country code ('44 7763233455' misread as local -> '+44447763233455')."""
    raw = (raw or '').strip()
    if not raw:
        return ''
    region = country_id if country_id and re.fullmatch(r'[A-Z]{2}', country_id) else None
    try:
        num = phonenumbers.parse(raw, region)
    except phonenumbers.NumberParseException:
        return ''
    if not phonenumbers.is_valid_number(num):
        return ''
    if phonenumbers.region_code_for_number(num) == '001':
        return ''  # non-geographic calling code (e.g. +979) — not a real dialable number
    return phonenumbers.format_number(num, phonenumbers.PhoneNumberFormat.E164)

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
    ap = argparse.ArgumentParser()
    ap.add_argument('--since', metavar='YYYY-MM-DD',
                     help="Delta mode: only customers whose 'updated_at' is on/after this date "
                          "(new accounts AND edits to older ones — see "
                          "05_DOCS/import/plan-migration.md, stratégie de synchro en 2 passes). "
                          "Writes to *_since_<date>.csv instead of the default files. "
                          "Omit for a full export.")
    args = ap.parse_args()

    output_dandoy, output_butterfly = OUTPUT_DANDOY, OUTPUT_BUTTERFLY
    if args.since:
        output_dandoy = output_dandoy.replace('.csv', f'_since_{args.since}.csv')
        output_butterfly = output_butterfly.replace('.csv', f'_since_{args.since}.csv')

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

    if args.since:
        cutoff = f"{args.since} 00:00:00"
        before = len(by_email)
        by_email = {e: c for e, c in by_email.items() if c.get('updated_at', '') >= cutoff}
        print(f"  --since {args.since}: {before} -> {len(by_email)} customers (updated_at >= {cutoff})")

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
    print("Writing Shopify CSVs…")
    counters = {
        'dandoy':    {'customers': 0, 'with_address': 0, 'no_address': 0,
                      'phone_dropped': 0, 'phone_deduped': 0, 'country_dropped': 0},
        'butterfly': {'customers': 0, 'with_address': 0, 'no_address': 0,
                      'phone_dropped': 0, 'phone_deduped': 0, 'country_dropped': 0},
    }
    seen_phones = {'dandoy': set(), 'butterfly': set()}
    spam_skipped = 0

    with open(output_dandoy, 'w', newline='', encoding='utf-8') as f_dandoy, \
         open(output_butterfly, 'w', newline='', encoding='utf-8') as f_butterfly:
        writers = {
            'dandoy':    csv.DictWriter(f_dandoy, fieldnames=SHOPIFY_COLS),
            'butterfly': csv.DictWriter(f_butterfly, fieldnames=SHOPIFY_COLS),
        }
        for w in writers.values():
            w.writeheader()

        for email, cust in by_email.items():
            firstname = cust.get('firstname', '').strip()
            lastname = cust.get('lastname', '').strip()
            if SPAM_NAME_RE.search(firstname) or SPAM_NAME_RE.search(lastname):
                spam_skipped += 1
                continue

            tags = sorted(cust.get('_tags', set()))

            # Find best address: prefer default billing, then default shipping,
            # skipping addresses in countries Shopify doesn't support (Matrixify
            # rejects the Country Code outright, so keeping such an address is
            # worse than falling back to the next one / no address at all).
            addresses = [a for a in addr_by_email.get(email, [])
                         if a.get('country_id', '').strip() not in UNSUPPORTED_COUNTRIES]
            country_dropped = len(addr_by_email.get(email, [])) > len(addresses)
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
            out['First Name'] = firstname
            out['Last Name'] = lastname
            out['Email'] = email
            out['Accepts Email Marketing'] = 'yes' if cust.get('is_review_booster_subscriber') == '1' else 'no'
            out['Tags'] = ','.join(tags)
            out['Tax Exempt'] = ''

            has_address = bool(best_addr)
            phone_dropped = False
            if best_addr:
                street = best_addr.get('street', '')
                lines = street.split('\n') if '\n' in street else [street]
                country_id = best_addr.get('country_id', '').strip()
                region_id = best_addr.get('region_id', '').strip()
                region = best_addr.get('region', '').strip()
                addr_phone = clean_phone(best_addr.get('telephone', ''), country_id)
                if best_addr.get('telephone', '').strip() and not addr_phone:
                    phone_dropped = True

                addr_first = best_addr.get('firstname', '').strip()
                addr_last = best_addr.get('lastname', '').strip()
                out['Address First Name'] = '' if SPAM_NAME_RE.search(addr_first) else addr_first
                out['Address Last Name'] = '' if SPAM_NAME_RE.search(addr_last) else addr_last
                out['Address Company'] = best_addr.get('company', '').strip()
                # Matrixify caps Address1 at 255 chars — a handful of rows
                # have ad/spam text glued onto the street line, well past
                # that limit.
                out['Address1'] = (lines[0].strip() if lines else '')[:255]
                out['Address2'] = lines[1].strip() if len(lines) > 1 else ''
                out['Address City'] = best_addr.get('city', '').strip()
                # See PROVINCE_SAFE_COUNTRIES above — only US region text
                # has proven to reliably match Shopify's province list.
                if (region and region_id not in ('', '0')
                        and country_id in PROVINCE_SAFE_COUNTRIES):
                    out['Address Province'] = region
                out['Address Country Code'] = country_id
                out['Address Zip'] = best_addr.get('postcode', '').strip()
                out['Address Phone'] = addr_phone
                out['Address Default'] = 'TRUE'

            # Phone from address if available; deduped per store since
            # Shopify enforces a unique Customer.phone (Address Phone isn't
            # constrained the same way).
            if not out['Phone'] and best_addr:
                out['Phone'] = addr_phone

            for store in tags:
                if store not in writers:
                    continue
                row = dict(out)
                if row['Phone']:
                    if row['Phone'] in seen_phones[store]:
                        row['Phone'] = ''
                        counters[store]['phone_deduped'] += 1
                    else:
                        seen_phones[store].add(row['Phone'])
                writers[store].writerow(row)
                counters[store]['customers'] += 1
                counters[store]['with_address' if has_address else 'no_address'] += 1
                if phone_dropped:
                    counters[store]['phone_dropped'] += 1
                if country_dropped:
                    counters[store]['country_dropped'] += 1

    print(f"\nDone.")
    for store in ('dandoy', 'butterfly'):
        c = counters[store]
        print(f"  [{store}] Customers exported      : {c['customers']}")
        print(f"  [{store}] With address            : {c['with_address']}")
        print(f"  [{store}] Without address         : {c['no_address']}")
        print(f"  [{store}] Unparseable phone dropped : {c['phone_dropped']}")
        print(f"  [{store}] Duplicate phone blanked   : {c['phone_deduped']}")
        print(f"  [{store}] Unsupported-country addr  : {c['country_dropped']}")
    print(f"\n  Spam accounts skipped (URL/HTML in name) : {spam_skipped}")
    print(f"\nOutput → {output_dandoy}")
    print(f"Output → {output_butterfly}")
    print(f"\n⚠  Passwords cannot be migrated — customers will need to reset via 'Forgot password'.")


if __name__ == '__main__':
    main()
