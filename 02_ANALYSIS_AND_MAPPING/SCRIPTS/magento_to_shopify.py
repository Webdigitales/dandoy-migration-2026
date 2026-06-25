#!/usr/bin/env python3
"""
Magento catalog_product CSV  →  Shopify products CSV (Matrixify format)
                               + Shopify translations CSV (Matrixify Translations format)

Rules:
- Only base store_view_code rows (= English / default prices)
- grouped product  → Shopify product with variants (one variant per child simple)
- simple product (standalone, not a grouped child) → Shopify product, single variant
- bundle / gift-card → skipped (logged)
- Images: full URL built from IMAGE_BASE + Magento path
- special_price present → Variant Price = special_price, Compare At = regular price
- product_online 1 = active, 2 = draft
- Variant options mapped per attribute_set (Handle, Color, Size, Thickness…)
- Product-level metafields extracted from additional_attributes
- Translations exported from eu_fr, eu_nl, bt_be_fr store views
"""

import csv
import re
import sys

INPUT       = '/home/gregory/Documents/Labo/dandoy/01_DATA_RAW/export_magento_products_all.csv'
OUTPUT      = '/home/gregory/Documents/Labo/dandoy/04_SHOPIFY_IMPORTS/shopify_products.csv'
OUTPUT_TR   = '/home/gregory/Documents/Labo/dandoy/04_SHOPIFY_IMPORTS/shopify_translations.csv'
IMAGE_BASE  = 'https://www.dandoy-sports.com/pub/media/catalog/product'


# ---------------------------------------------------------------------------
# Option mapping per attribute_set
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
    'Migration_Tables and Nets': [
        ('Color', '_name_suffix', None),
    ],
    'Migration_Default': [
        ('Size', 'size', None),
    ],
}


# ---------------------------------------------------------------------------
# Metafield mapping: Magento attribute → Shopify metafield
# ---------------------------------------------------------------------------

METAFIELD_MAP = {
    'promotion_type':       ('custom.promotion',        'list.single_line_text_field', True),
    'blades_type':          ('custom.blade_category',   'single_line_text_field', False),
    'blades_layers':        ('custom.blade_layers',     'single_line_text_field', False),
    'blades_feeling':       ('custom.blade_feeling',    'single_line_text_field', False),
    'rubbers_type':         ('custom.rubber_category',  'single_line_text_field', False),
    'rubbers_pimples':      ('custom.pimples',          'single_line_text_field', False),
    'rubbers_hardness':     ('custom.hardness',         'single_line_text_field', False),
    'technology_stiga':     ('custom.technology',        'list.single_line_text_field', True),
    'technology_butterfly': ('custom.technology',        'list.single_line_text_field', True),
    'gender':               ('custom.gender',            'list.single_line_text_field', True),
    'shoes_type':           ('custom.shoe_type',         'list.single_line_text_field', True),
    'bags_model':           ('custom.bag_model',         'single_line_text_field', False),
    'balls_usage':          ('custom.ball_usage',        'single_line_text_field', False),
    'balls_material':       ('custom.ball_material',     'single_line_text_field', False),
    'usage':                ('custom.usage',             'single_line_text_field', False),
    'accessories':          ('custom.accessory_type',    'single_line_text_field', False),
    'tables_type':          ('custom.environment',       'single_line_text_field', False),
    'cover':                ('custom.cover_included',    'boolean',                False),
    'dimension':            ('custom.dimension',         'single_line_text_field', False),
    'videos':               ('custom.video_url',         'url',                    False),
}


def _build_metafield_columns():
    seen = {}
    for mkey, mtype, _ in METAFIELD_MAP.values():
        if mkey not in seen:
            seen[mkey] = mtype
    return [f"Metafield: {k} [{v}]" for k, v in seen.items()]

METAFIELD_COLS = _build_metafield_columns()

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
    'Variant Image',
    'Gift Card', 'SEO Title', 'SEO Description', 'Status',
] + METAFIELD_COLS

# ---------------------------------------------------------------------------
# Translation config
#
# Store view priority per language:
#   FR: bt_be_fr (Butterfly own) → eu_fr (Dandoy, shared) → skip
#   NL: eu_nl (main source) → skip
#
# bt_be_nl and bt_nl are too incomplete to be useful.
# eu_en and ww_en contain no real translations.
# ---------------------------------------------------------------------------

TRANSLATION_COLS = [
    'Entity', 'Entity Handle', 'Field',
    'Translation Value: fr', 'Translation Value: nl',
]

TRANSLATABLE_FIELDS = [
    ('title',            'name'),
    ('body_html',        'description'),
]


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


SUBCATEGORY_TAG_MAP = {
    'Clothing/Polos':               'polos',
    'Clothing/Shorts':              'shorts',
    'Clothing/T-shirts':            't-shirts',
    'Clothing/Jackets':             'jackets',
    'Clothing/Socks':               'socks',
    'Clothing/Suits':               'suits',
    'Clothing/Sweater':             'sweater',
    'Luggages/Bags':                'bags',
    'Luggages/Batcover':            'batcover',
    'Tables & Nets/Tables':         'tables',
    'Tables & Nets/Nets':           'nets',
    'Cleaners & Glue/Cleaners':     'cleaners',
    'Cleaners & Glue/Glue':         'glue',
    'Rubbers/Colours rubbers':      'colours-rubbers',
    'Robots/Robots':                'robots-machines',
    'Robots/Accessories':           'robots-accessories',
    'Accessories/Rackets':          'accessories-rackets',
    'Accessories/Textiles':         'accessories-textiles',
    'Accessories/Robots':           'accessories-robots',
    'Liquidations Football/Maillot': 'football-maillot',
    'Liquidations Football/Short':  'football-short',
    'Liquidations Football/Bas':    'football-bas',
}


def categories_to_tags(categories_str):
    tags = set()
    for cat_path in (categories_str or '').split(','):
        parts = [p.strip() for p in cat_path.strip().split('/') if p.strip() != 'All']
        for part in parts:
            if part and part.lower() not in ('all', 'default category', ''):
                tags.add(part)
        subpath = '/'.join(parts)
        if subpath in SUBCATEGORY_TAG_MAP:
            tags.add(SUBCATEGORY_TAG_MAP[subpath])
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
    attrs = parse_additional_attrs(child_row.get('additional_attributes', ''))
    suffix = name_suffix(parent_row.get('name', ''), child_row.get('name', child_row['sku']))
    result = {}

    slot = 1
    for opt_name, source, transform in option_defs[:3]:
        if source == '_name_suffix':
            raw = suffix
        elif source == '_name_suffix_numeric':
            raw = extract_numeric(suffix)
        else:
            raw = attrs.get(source, '')

        if transform and raw:
            raw = transform(raw)

        if not raw:
            continue

        result[f'Option{slot} Name'] = opt_name
        result[f'Option{slot} Value'] = raw
        slot += 1

    return result


def resolve_metafields(row):
    attrs = parse_additional_attrs(row.get('additional_attributes', ''))
    result = {col: '' for col in METAFIELD_COLS}

    merged = {}
    for mag_key, (mf_key, mf_type, is_list) in METAFIELD_MAP.items():
        raw = attrs.get(mag_key, '')
        if not raw:
            continue

        col_name = f"Metafield: {mf_key} [{mf_type}]"

        if mf_type == 'boolean':
            val = 'true' if raw.lower() in ('yes', '1', 'true') else 'false'
            result[col_name] = val
        elif is_list:
            items = [v.strip() for v in raw.split('|') if v.strip()]
            if col_name in merged:
                merged[col_name].extend(items)
            else:
                merged[col_name] = items
        else:
            result[col_name] = raw

    for col_name, items in merged.items():
        seen = []
        for item in items:
            if item not in seen:
                seen.append(item)
        result[col_name] = ';'.join(seen)

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
    # ------------------------------------------------------------------
    # Pass 1: Load ALL rows, indexed by (sku, store_view_code)
    # ------------------------------------------------------------------
    print("Loading CSV…")
    all_by_sku_sv = {}   # (sku, store_view_code) → row
    base_rows = {}       # sku → row  (base store only)

    with open(INPUT, encoding='utf-8') as f:
        for row in csv.DictReader(f):
            sv = row.get('store_view_code', '') or ''
            sku = row['sku']
            all_by_sku_sv[(sku, sv)] = row
            if sv == '' and sku not in base_rows:
                base_rows[sku] = row

    print(f"  Total rows loaded: {len(all_by_sku_sv)}")
    print(f"  Base rows: {len(base_rows)}")

    grouped_child_skus = set()
    for row in base_rows.values():
        if row['product_type'] == 'grouped':
            for sp in (row.get('associated_skus', '') or '').split(','):
                child = sp.split('=')[0].strip()
                if child:
                    grouped_child_skus.add(child)

    print(f"  Grouped children: {len(grouped_child_skus)}")
    print(f"  Metafield columns: {len(METAFIELD_COLS)}")

    # ------------------------------------------------------------------
    # Pass 2: Write products CSV (same as before)
    # ------------------------------------------------------------------
    print("\nWriting products CSV…")
    counters = {'products': 0, 'rows': 0, 'skipped': 0}
    skipped_types = {}
    fallback_count = 0
    exported_handles = {}  # sku → handle (for translations)

    with open(OUTPUT, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=SHOPIFY_COLS)
        writer.writeheader()

        for sku, row in base_rows.items():
            pt = row['product_type']
            handle = (row.get('url_key', '') or sku).strip()

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
                mfields = resolve_metafields(row)
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
                        out.update(mfields)
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

                exported_handles[sku] = handle
                counters['products'] += 1

            elif pt == 'simple' and sku not in grouped_child_skus:
                images  = collect_images(row)
                mfields = resolve_metafields(row)
                out     = blank()
                out.update(product_fields(row, handle))
                out.update(variant_fields(row))
                out.update(mfields)
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

                exported_handles[sku] = handle
                counters['products'] += 1

            else:
                skipped_types[pt] = skipped_types.get(pt, 0) + 1
                counters['skipped'] += 1

    print(f"  Products written : {counters['products']}")
    print(f"  CSV rows written : {counters['rows']}")
    print(f"  Skipped          : {counters['skipped']}")
    if skipped_types:
        for t, n in skipped_types.items():
            print(f"    └─ {t}: {n}")
    if fallback_count:
        print(f"  Fallback (name suffix) : {fallback_count} grouped products")
    print(f"  Output → {OUTPUT}")

    # ------------------------------------------------------------------
    # Pass 3: Write translations CSV
    # ------------------------------------------------------------------
    print("\nWriting translations CSV…")
    tr_counters = {'rows': 0, 'products_fr': 0, 'products_nl': 0}

    def get_translation(sku, store_view, field):
        """Get a translated field value from a specific store view."""
        row = all_by_sku_sv.get((sku, store_view))
        if row:
            return (row.get(field, '') or '').strip()
        return ''

    def get_fr(sku, field):
        """FR: try bt_be_fr first (Butterfly own), then eu_fr (Dandoy/shared)."""
        val = get_translation(sku, 'bt_be_fr', field)
        if val:
            return val
        return get_translation(sku, 'eu_fr', field)

    def get_nl(sku, field):
        """NL: eu_nl is the main source."""
        return get_translation(sku, 'eu_nl', field)

    with open(OUTPUT_TR, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=TRANSLATION_COLS)
        writer.writeheader()

        for sku, handle in exported_handles.items():
            has_fr = False
            has_nl = False

            for shopify_field, magento_field in TRANSLATABLE_FIELDS:
                fr_val = get_fr(sku, magento_field)
                nl_val = get_nl(sku, magento_field)

                if magento_field == 'description':
                    if fr_val:
                        fr_val = fr_val.replace('\n', '<br>\n')
                    if nl_val:
                        nl_val = nl_val.replace('\n', '<br>\n')

                if fr_val or nl_val:
                    row = {
                        'Entity':                 'Product',
                        'Entity Handle':          handle,
                        'Field':                  shopify_field,
                        'Translation Value: fr':  fr_val,
                        'Translation Value: nl':  nl_val,
                    }
                    writer.writerow(row)
                    tr_counters['rows'] += 1

                    if fr_val:
                        has_fr = True
                    if nl_val:
                        has_nl = True

            if has_fr:
                tr_counters['products_fr'] += 1
            if has_nl:
                tr_counters['products_nl'] += 1

    print(f"  Translation rows  : {tr_counters['rows']}")
    print(f"  Products with FR  : {tr_counters['products_fr']}")
    print(f"  Products with NL  : {tr_counters['products_nl']}")
    print(f"  Output → {OUTPUT_TR}")

    print("\nDone.")


if __name__ == '__main__':
    main()
