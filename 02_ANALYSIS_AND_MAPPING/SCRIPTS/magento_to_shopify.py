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
    'tables_type':          ('custom.environment',       'list.single_line_text_field', True),
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

# Free custom options (Gluing / Edge tape / Lacquering) come from the
# `custom_options` column, not `additional_attributes` — parsed separately
# below and merged in as their own list metafield. Drives which line item
# property selectors the theme shows per product, since the option set
# varies within a product Type (e.g. 15.6% of Rubbers have none at all).
CUSTOM_OPTIONS_METAFIELD_COL = 'Metafield: custom.available_options [list.single_line_text_field]'

_CUSTOM_OPTION_PATTERNS = [
    (re.compile(r'lacquer|vernis', re.I), 'Lacquering'),
    (re.compile(r'gluing|collage|lijmen|coller', re.I), 'Gluing'),
    (re.compile(r'edge|tape|bord|contour|afplak', re.I), 'EdgeTape'),
]

def extract_custom_options(row):
    raw = (row.get('custom_options', '') or '').strip()
    if not raw:
        return []
    names = re.findall(r'name=([^,]*),type=', raw)
    result = []
    for n in names:
        for pattern, canon in _CUSTOM_OPTION_PATTERNS:
            if pattern.search(n) and canon not in result:
                result.append(canon)
                break
    return result


METAFIELD_COLS = _build_metafield_columns() + [CUSTOM_OPTIONS_METAFIELD_COL]

SHOPIFY_COLS = [
    'Handle', 'Command', 'Title', 'Body (HTML)', 'Vendor', 'Product Category', 'Type',
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


# Rubbers: color is sometimes missing from additional_attributes (~8% of
# variants) but always present in the product name — in English or Dutch
# (Butterfly base names are in NL). Used as a fallback so every variant of
# a product gets a Color value; otherwise some variants end up with an
# empty Option1 while siblings have one, which Matrixify rejects.
COLOR_NAME_MAP = {
    'Red': ['Red', 'Rood'],
    'Black': ['Black', 'Zwart'],
    'Blue': ['Blue', 'Blauw'],
    'Green': ['Green', 'Groen'],
    'Pink': ['Pink', 'Roze'],
    'Purple': ['Purple', 'Paars'],
}


def extract_color_from_name(suffix):
    for canon, variants in COLOR_NAME_MAP.items():
        for variant in variants:
            if re.search(r'\b' + variant + r'\b', suffix, re.IGNORECASE):
                return canon
    return ''


# Rubbers: thickness is the last word of the name suffix — usually numeric
# (1.0, 1.5, 2.1…) but also non-numeric grades used in table tennis rubbers
# (OX = no sponge, Max/Max+ = maximum allowed, Thin/Middle/Thick/Super Thick).
# A trailing parenthetical note (e.g. "(Sponge Dampening)") is stripped first.
def extract_thickness(suffix):
    s = (suffix or '').strip()
    s = re.sub(r'\s*\([^)]*\)\s*$', '', s)
    m = re.search(r'(\d+\.?\d*)$', s)
    if m:
        return m.group(1)
    m = re.search(r'(super thick|max\+|thin|middle|thick|max|ox)$', s, re.IGNORECASE)
    return m.group(1).title() if m else ''


def resolve_options(parent_row, child_row, option_defs, prefer_suffix=False):
    attrs = parse_additional_attrs(child_row.get('additional_attributes', ''))
    suffix = name_suffix(parent_row.get('name', ''), child_row.get('name', child_row['sku']))
    result = {}

    # Fixed slot per option_defs position (not per how many values were
    # found) — otherwise a variant missing e.g. Color shifts Thickness into
    # Option1 while sibling variants keep it in Option2, which Matrixify
    # rejects as an inconsistent option schema for the same product.
    for slot, (opt_name, source, transform) in enumerate(option_defs[:3], start=1):
        suffix_val = re.sub(r'^size\s+', '', suffix, flags=re.IGNORECASE)

        if source == '_name_suffix':
            raw = suffix
        elif source == '_name_suffix_numeric':
            raw = extract_thickness(suffix)
        elif source == 'color':
            name_color = extract_color_from_name(suffix)
            # prefer_suffix: a sibling variant collided using the attribute
            # value, so trust the name over a possibly wrong/reused
            # attribute value (e.g. same Magento size/color enum value
            # reused across genuinely different variants).
            raw = (name_color or attrs.get('color', '')) if prefer_suffix else (attrs.get('color', '') or name_color)
        else:
            # Some product lines (socks, sweatshirts…) don't populate this
            # attribute at all on part of the range, even though the value
            # is visible in the child name (e.g. "Size I (35-38)", "RIO Red
            # 6"). Falling back to the raw suffix keeps every variant of the
            # product non-empty and distinct instead of silently colliding.
            raw = (suffix_val or attrs.get(source, '')) if prefer_suffix else (attrs.get(source, '') or suffix_val)

        if transform and raw:
            raw = transform(raw)

        if not raw:
            continue

        result[f'Option{slot} Name'] = opt_name
        result[f'Option{slot} Value'] = raw

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

    custom_opts = extract_custom_options(row)
    if custom_opts:
        result[CUSTOM_OPTIONS_METAFIELD_COL] = ';'.join(custom_opts)

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
        'Command':         'MERGE',
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
    used_handles = {}      # handle → sku that first claimed it
    handle_collisions = [] # (original_handle, first_sku, colliding_sku, new_handle)
    option_dup_warnings = []  # (handle, first_sku, colliding_sku, option_values) still duplicate after retry

    with open(OUTPUT, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=SHOPIFY_COLS)
        writer.writeheader()

        for sku, row in base_rows.items():
            pt = row['product_type']
            handle = (row.get('url_key', '') or sku).strip()
            # A grouped product's own simple children legitimately share its
            # url_key (they never become standalone Shopify products, they
            # get folded into the parent's variant rows) — only products that
            # are actually written under their own Handle can collide.
            is_written_standalone = pt == 'grouped' or (pt == 'simple' and sku not in grouped_child_skus)

            # Some distinct Magento products share the same url_key (source
            # data bug, e.g. "Donic Burn Off" and "Donic Burn Off -" both use
            # url_key=donic-burn-off). Writing both under one Shopify Handle
            # merges their variants and fails Matrixify import ("variant
            # already exists" / Title-Body HTML differ). Disambiguate the
            # 2nd+ product instead — flagged below for manual SEO review.
            if is_written_standalone:
                if handle in used_handles:
                    n = 2
                    new_handle = f'{handle}-{n}'
                    while new_handle in used_handles:
                        n += 1
                        new_handle = f'{handle}-{n}'
                    handle_collisions.append((handle, used_handles[handle], sku, new_handle))
                    handle = new_handle
                used_handles[handle] = sku

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
                # custom_options (Gluing/EdgeTape/Lacquering) live on the
                # child simple SKUs, not the grouped parent — union them so
                # the product-level metafield reflects any child that needs
                # the selector on the product page.
                child_custom_opts = []
                for child in children:
                    for opt in extract_custom_options(child):
                        if opt not in child_custom_opts:
                            child_custom_opts.append(opt)
                if child_custom_opts:
                    mfields[CUSTOM_OPTIONS_METAFIELD_COL] = ';'.join(child_custom_opts)
                img_pos = 1
                first   = True

                # Resolve every child's options up front so duplicates across
                # siblings can be caught and retried before writing — some
                # Magento SKUs reuse the same attribute value (e.g. size=XXS
                # for both "6 yo" and "8 yo" children) or have an attribute
                # that plainly contradicts the product name. Retrying with
                # the name-derived value resolves most of these; the rest are
                # genuine source-data duplicates flagged for manual review.
                child_opts = {}
                if option_defs:
                    seen_combos = {}
                    for child in children:
                        opts = resolve_options(row, child, option_defs)
                        key = tuple(opts.get(f'Option{i} Value', '') for i in (1, 2, 3))
                        if key in seen_combos:
                            retry = resolve_options(row, child, option_defs, prefer_suffix=True)
                            retry_key = tuple(retry.get(f'Option{i} Value', '') for i in (1, 2, 3))
                            if retry_key not in seen_combos:
                                opts, key = retry, retry_key
                            else:
                                option_dup_warnings.append((handle, seen_combos[key], child['sku'], key))
                        seen_combos[key] = child['sku']
                        child_opts[child['sku']] = opts

                for child in children:
                    out = blank()
                    out.update(variant_fields(child))
                    out['Handle']      = handle
                    out['Variant SKU'] = child['sku']

                    if option_defs:
                        out.update(child_opts[child['sku']])
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
    if handle_collisions:
        print(f"  ⚠ Handle collisions renommés : {len(handle_collisions)} (à valider manuellement — impact SEO/redirections)")
        for orig, first_sku, dup_sku, new_handle in handle_collisions:
            print(f"    └─ '{orig}' : {first_sku} garde le handle, {dup_sku} → '{new_handle}'")
    if option_dup_warnings:
        print(f"  ⚠ Variantes dupliquées non résolues : {len(option_dup_warnings)} (donnée source à corriger manuellement)")
        for handle_, first_sku, dup_sku, key in option_dup_warnings:
            print(f"    └─ '{handle_}' : {first_sku} et {dup_sku} ont la même combinaison d'options {key}")
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
