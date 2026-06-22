#!/usr/bin/env python3
"""
Generate 301 redirect map: Magento URLs → Shopify URLs

Only redirect URLs that are actually LIVE on Magento:
- product_online = 1 (active)
- visibility = "Catalog, Search" or "Catalog" (visible, not "Not Visible Individually")

Types of redirects:
1. Active grouped parent:    /{url_key}.html → /products/{handle}
2. Active standalone simple: /{url_key}.html → /products/{handle}
3. url_path aliases:         /{url_path}.html → /products/{handle}  (when url_path ≠ url_key)
4. Categories:               /{slug}.html → /collections/{slug}

NOT redirected (already 404 on Magento):
- Child simple products (visibility = Not Visible Individually)
- Disabled products (product_online = 2)

Output: Matrixify Redirects CSV format (Redirect From, Redirect To)
"""

import csv

INPUT  = '/home/gregory/Documents/Labo/dandoy/01_DATA_RAW/export_magento_products_all.csv'
OUTPUT = '/home/gregory/Documents/Labo/dandoy/03_SEO_AND_REDIRECTS/shopify_redirects.csv'

REDIRECT_COLS = ['Redirect From', 'Redirect To']


def parse_attrs(s):
    attrs = {}
    for pair in (s or '').split(','):
        if '=' in pair:
            k, _, v = pair.partition('=')
            attrs[k.strip()] = v.strip()
    return attrs


def is_visible(row):
    vis = row.get('visibility', '')
    return vis in ('Catalog, Search', 'Catalog', 'Search')


def is_active(row):
    return row.get('product_online', '') == '1'


def main():
    print("Loading CSV…")
    base_rows = {}
    with open(INPUT, encoding='utf-8') as f:
        for row in csv.DictReader(f):
            if row.get('store_view_code', '') == '':
                sku = row['sku']
                if sku not in base_rows:
                    base_rows[sku] = row

    print(f"  Base rows: {len(base_rows)}")

    # --- Product redirects (active + visible only) ---
    redirects = []
    seen_from = set()
    skipped = {'inactive': 0, 'invisible': 0}

    def add_redirect(old_path, new_path):
        if old_path and old_path not in seen_from and old_path != new_path:
            redirects.append((old_path, new_path))
            seen_from.add(old_path)

    for sku, row in base_rows.items():
        pt = row['product_type']
        if pt not in ('grouped', 'simple'):
            continue

        if not is_active(row):
            skipped['inactive'] += 1
            continue
        if not is_visible(row):
            skipped['invisible'] += 1
            continue

        url_key = row.get('url_key', '').strip()
        attrs = parse_attrs(row.get('additional_attributes', ''))
        url_path = attrs.get('url_path', '').strip()
        handle = url_key
        target = f"/products/{handle}"

        add_redirect(f"/{url_key}.html", target)
        if url_path and url_path != url_key:
            add_redirect(f"/{url_path}.html", target)

    product_count = len(redirects)

    # --- Category redirects ---
    cat_slugs = set()
    for row in base_rows.values():
        for cat_path in row.get('categories', '').split(','):
            parts = cat_path.strip().split('/')
            for part in parts:
                name = part.strip()
                slug = name.lower().replace(' & ', '-').replace(' ', '-')
                if slug and slug != 'all':
                    cat_slugs.add((name, slug))

    for name, slug in cat_slugs:
        add_redirect(f"/{slug}.html", f"/collections/{slug}")

    category_count = len(redirects) - product_count

    # --- Write CSV ---
    with open(OUTPUT, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=REDIRECT_COLS)
        writer.writeheader()
        for old, new in redirects:
            writer.writerow({'Redirect From': old, 'Redirect To': new})

    print(f"\nDone.")
    print(f"  Product redirects  : {product_count}")
    print(f"  Category redirects : {category_count}")
    print(f"  Total redirects    : {len(redirects)}")
    print(f"  Skipped (inactive) : {skipped['inactive']}")
    print(f"  Skipped (invisible): {skipped['invisible']}")
    print(f"\nOutput → {OUTPUT}")


if __name__ == '__main__':
    main()
