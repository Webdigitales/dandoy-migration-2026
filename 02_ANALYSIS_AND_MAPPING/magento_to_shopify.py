#!/usr/bin/env python3
"""
Magento catalog_product CSV  →  Shopify products CSV

Rules:
- Only base store_view_code rows (= English / default prices)
- grouped product  → Shopify product with variants (one variant per child simple)
- simple product (standalone, not a grouped child) → Shopify product, single variant
- bundle / gift-card → skipped (logged)
- Images: full URL built from IMAGE_BASE + Magento path
- special_price present → Variant Price = special_price, Compare At = regular price
- product_online 1 = active, 2 = draft
- Variant options mapped per attribute_set (Handle, Color, Size, Thickness…)
"""

import csv
import re
import sys

INPUT      = '/home/gregory/Documents/Labo/dandoy/01_DATA_RAW/export_magento_products_all.csv'
OUTPUT     = '/home/gregory/Documents/Labo/dandoy/04_SHOPIFY_IMPORTS/shopify_products.csv'
IMAGE_BASE = 'https://www.dandoy-sports.com/pub/media/catalog/product'

SHOPIFY_COLS = [
    'Handle', 'Title', 'Body (HTML)', 'Vendor', 'Product Category', 'Type',
    'Tags', 'Published',
    'Option1 Name', 'Option1 Value',
    'Option2 Name', 'Option2 Value',
    'Option3 Name', 'Option3 Value',
    'Variant SKU', 'Variant Grams',
    'Variant Inventory Tracker', 'Variant Inventory Qty',
    'Variant Inventory Policy', 'Variant Fulfillment Service',
    'Variant Price', 'Variant Compare At Price',
    'Variant Requires Shipping', 'Variant Taxable',
    'Variant Barcode',
    'Image Src', 'Image Position', 'Image Alt Text',
    'Gift Card', 'SEO Title', 'SEO Description', 'Status',
]

# ---------------------------------------------------------------------------
# Option mapping per attribute_set
#
# Each entry: list of (shopify_option_name, source, transform_fn)
#   source = attribute key in additional_attributes, or special:
#     '_name_suffix'         → child name minus parent name
#     '_name_suffix_numeric' → numeric part extracted from name suffix
#   transform_fn = None (use raw) or callable(value) → cleaned value
# ---------------------------------------------------------------------------

def _clean_handle(v):
    return v.replace('handle-', '').replace('handle_', '').title()

def _strip_eu(v):
    return v.replace('EU', '')

OPTION_MAP = {
    'Migration_Blades': [
        ('Handle', 'baldes_handles', _clean_handle),
    ],
    'Migration_Rubbers': [
        ('Color', 'color', str.title),
        ('Thickness', '_name_suffix_numeric', None),
    ],
    'Migration_Clothing': [
        ('Size', 'size', None),
    ],
    'Migration_Shoes': [
        ('Size', 'size_shoes', _strip_eu),
    ],
    'Migration_Bags': [
        ('Color', 'color', str.title),
    ],
    'Migration_Balls': [
        ('Quantity', 'balls_quantity', None),
        ('Color', 'color', str.title),
    ],
    'Migration_Cleaners': [
        ('Quantity', 'quantity', None),
    ],
    'Migration_Default': [
        ('Size', 'size', None),
    ],
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parse_additional_attrs(s):
    attrs = {}
    for pair in (s or '').split(','):
        if '=' in pair:
            k, _, v = pair.partition('=')
            attrs[k.strip()] = v.strip()
    return attrs


def image_url(path):
    if not path:
        return ''
    path = path.strip()
    if not path:
        return ''
    return IMAGE_BASE + (path if path.startswith('/') else '/' + path)


def collect_images(row):
    seen = set()
    imgs = []
    for path in [row.get('base_image', '')] + (row.get('additional_images', '') or '').split(','):
        url = image_url(path)
        if url and url not in seen:
            seen.add(url)
            imgs.append(url)
    return imgs


def to_grams(weight_str):
    try:
        return str(int(float(weight_str) * 1000))
    except (ValueError, TypeError):
        return ''


def categories_to_tags(categories_str):
    tags = set()
    for part in (categories_str or '').replace('/', ',').split(','):
        part = part.strip()
        if part and part.lower() not in ('all', 'default category', ''):
            tags.add(part)
    return ','.join(sorted(tags))


def name_suffix(parent_name, child_name):
    p = (parent_name or '').strip()
    c = (child_name or '').strip()
    if c.startswith(p):
        suffix = c[len(p):].strip()
        return suffix if suffix else c
    return c


def extract_numeric(s):
    m = re.search(r'(\d+\.?\d*)', s or '')
    return m.group(1) if m else ''


def resolve_options(parent_row, child_row, option_defs):
    """Resolve Shopify Option1/2/3 from a child row using option definitions."""
    attrs = parse_additional_attrs(child_row.get('additional_attributes', ''))
    suffix = name_suffix(parent_row.get('name', ''), child_row.get('name', child_row['sku']))
    result = {}

    for i, (opt_name, source, transform) in enumerate(option_defs[:3], 1):
        if source == '_name_suffix':
            raw = suffix
        elif source == '_name_suffix_numeric':
            raw = extract_numeric(suffix)
        else:
            raw = attrs.get(source, '')

        if transform and raw:
            raw = transform(raw)

        result[f'Option{i} Name'] = opt_name
        result[f'Option{i} Value'] = raw if raw else ''

    return result


def prices(row):
    raw     = (row.get('price', '') or '').strip()
    special = (row.get('special_price', '') or '').strip()
    if special:
        return special, raw
    return raw, ''


def status(row):
    return 'active' if row.get('product_online', '1') == '1' else 'draft'


def published(row):
    return 'TRUE' if row.get('product_online', '1') == '1' else 'FALSE'


def blank():
    return {col: '' for col in SHOPIFY_COLS}


def variant_fields(row):
    vp, ca = prices(row)
    backorders = row.get('allow_backorders', '0') or '0'
    try:
        qty = str(int(float(row.get('qty', '0') or '0')))
    except ValueError:
        qty = '0'
    return {
        'Variant Grams':             to_grams(row.get('weight', '')),
        'Variant Inventory Tracker': 'shopify',
        'Variant Inventory Qty':     qty,
        'Variant Inventory Policy':  'continue' if backorders == '1' else 'deny',
        'Variant Fulfillment Service': 'manual',
        'Variant Price':             vp,
        'Variant Compare At Price':  ca,
        'Variant Requires Shipping': 'TRUE',
        'Variant Taxable':           'TRUE' if row.get('tax_class_name', '') else 'FALSE',
    }


def product_fields(row, handle):
    attrs  = parse_additional_attrs(row.get('additional_attributes', ''))
    vendor = attrs.get('manufacturer', '')
    desc   = (row.get('description', '') or '').replace('\n', '<br>\n')
    ptype  = (row.get('attribute_set_code', '') or '').replace('Migration_', '')
    return {
        'Handle':          handle,
        'Title':           row.get('name', ''),
        'Body (HTML)':     desc,
        'Vendor':          vendor,
        'Product Category': '',
        'Type':            ptype,
        'Tags':            categories_to_tags(row.get('categories', '')),
        'Published':       published(row),
        'Gift Card':       'FALSE',
        'SEO Title':       (row.get('meta_title', '') or row.get('name', '')).strip(),
        'SEO Description': (row.get('meta_description', '') or '').strip(),
        'Status':          status(row),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("Loading CSV…")
    base_rows = {}
    with open(INPUT, encoding='utf-8') as f:
        for row in csv.DictReader(f):
            if row.get('store_view_code', '') == '':
                sku = row['sku']
                if sku not in base_rows:
                    base_rows[sku] = row

    print(f"  Base rows loaded: {len(base_rows)}")

    grouped_child_skus = set()
    for row in base_rows.values():
        if row['product_type'] == 'grouped':
            for sp in (row.get('associated_skus', '') or '').split(','):
                child = sp.split('=')[0].strip()
                if child:
                    grouped_child_skus.add(child)

    print(f"  Grouped children: {len(grouped_child_skus)}")

    counters = {'products': 0, 'rows': 0, 'skipped': 0}
    skipped_types = {}
    fallback_count = 0

    with open(OUTPUT, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=SHOPIFY_COLS)
        writer.writeheader()

        for sku, row in base_rows.items():
            pt = row['product_type']
            handle = (row.get('url_key', '') or sku).strip()

            # --- Grouped → product with variants ---
            if pt == 'grouped':
                child_skus = [s.split('=')[0].strip()
                              for s in (row.get('associated_skus', '') or '').split(',')
                              if s.strip()]
                children = [base_rows[s] for s in child_skus if s in base_rows]
                if not children:
                    counters['skipped'] += 1
                    continue

                aset = row.get('attribute_set_code', '')
                option_defs = OPTION_MAP.get(aset)
                uses_fallback = option_defs is None
                if uses_fallback:
                    fallback_count += 1

                images  = collect_images(row)
                pfields = product_fields(row, handle)
                img_pos = 1
                first   = True

                for child in children:
                    out = blank()
                    out.update(variant_fields(child))
                    out['Handle']      = handle
                    out['Variant SKU'] = child['sku']

                    if option_defs:
                        opts = resolve_options(row, child, option_defs)
                        out.update(opts)
                    else:
                        out['Option1 Name']  = 'Title'
                        out['Option1 Value'] = name_suffix(
                            row.get('name', ''), child.get('name', child['sku']))

                    if first:
                        out.update(pfields)
                        if images:
                            out['Image Src']      = images[0]
                            out['Image Position'] = '1'
                            img_pos = 2
                        first = False
                    else:
                        if img_pos <= len(images):
                            out['Image Src']      = images[img_pos - 1]
                            out['Image Position'] = str(img_pos)
                            img_pos += 1

                    writer.writerow(out)
                    counters['rows'] += 1

                while img_pos <= len(images):
                    out = blank()
                    out['Handle']         = handle
                    out['Image Src']      = images[img_pos - 1]
                    out['Image Position'] = str(img_pos)
                    writer.writerow(out)
                    img_pos += 1
                    counters['rows'] += 1

                counters['products'] += 1

            # --- Standalone simple ---
            elif pt == 'simple' and sku not in grouped_child_skus:
                images = collect_images(row)
                out    = blank()
                out.update(product_fields(row, handle))
                out.update(variant_fields(row))
                out['Option1 Name']  = 'Title'
                out['Option1 Value'] = 'Default Title'
                out['Variant SKU']   = sku
                if images:
                    out['Image Src']      = images[0]
                    out['Image Position'] = '1'
                writer.writerow(out)
                counters['rows'] += 1

                for pos, img in enumerate(images[1:], 2):
                    img_out = blank()
                    img_out['Handle']         = handle
                    img_out['Image Src']      = img
                    img_out['Image Position'] = str(pos)
                    writer.writerow(img_out)
                    counters['rows'] += 1

                counters['products'] += 1

            # --- Skipped types ---
            else:
                skipped_types[pt] = skipped_types.get(pt, 0) + 1
                counters['skipped'] += 1

    print(f"\nDone.")
    print(f"  Products written : {counters['products']}")
    print(f"  CSV rows written : {counters['rows']}")
    print(f"  Skipped          : {counters['skipped']}")
    if skipped_types:
        for t, n in skipped_types.items():
            print(f"    └─ {t}: {n}")
    if fallback_count:
        print(f"  Fallback (name suffix) : {fallback_count} grouped products")
    print(f"\nOutput → {OUTPUT}")


if __name__ == '__main__':
    main()
