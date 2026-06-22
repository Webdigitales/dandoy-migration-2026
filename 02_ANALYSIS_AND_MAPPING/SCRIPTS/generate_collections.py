#!/usr/bin/env python3
"""
Generate Shopify Smart Collections CSV for Matrixify import.

Each collection uses rules based on Product Type and/or Product Tag.
Multi-rule collections use additional rows with the same Handle.
"""

import csv

OUTPUT = '/home/gregory/Documents/Labo/dandoy/04_SHOPIFY_IMPORTS/shopify_collections.csv'

COLS = [
    'Handle', 'Command', 'Title', 'Body HTML', 'Published', 'Sort Order',
    'Must Match', 'Rule: Column', 'Rule: Relation', 'Rule: Condition',
]

# ---------------------------------------------------------------------------
# Collection definitions
#
# (handle, title, must_match, rules)
#   rules = list of (column, relation, condition)
#   must_match = "all conditions" or "any condition"
# ---------------------------------------------------------------------------

COLLECTIONS = [
    # --- Top-level ---
    ('blades', 'Blades', 'all conditions', [
        ('Product type', 'equals', 'Blades'),
    ]),
    ('rubbers', 'Rubbers', 'all conditions', [
        ('Product type', 'equals', 'Rubbers'),
    ]),
    ('clothing', 'Clothing', 'all conditions', [
        ('Product type', 'equals', 'Clothing'),
    ]),
    ('shoes', 'Shoes', 'all conditions', [
        ('Product type', 'equals', 'Shoes'),
    ]),
    ('luggages', 'Luggages', 'all conditions', [
        ('Product type', 'equals', 'Bags'),
    ]),
    ('balls', 'Balls', 'all conditions', [
        ('Product type', 'equals', 'Balls'),
    ]),
    ('tables-nets', 'Tables & Nets', 'all conditions', [
        ('Product type', 'equals', 'Tables and Nets'),
    ]),
    ('rackets', 'Rackets', 'all conditions', [
        ('Product type', 'equals', 'Rackets'),
    ]),
    ('robots', 'Robots', 'all conditions', [
        ('Product type', 'equals', 'Robots'),
    ]),
    ('accessories', 'Accessories', 'all conditions', [
        ('Product type', 'equals', 'Accessories'),
    ]),
    ('cleaners-glue', 'Cleaners & Glue', 'all conditions', [
        ('Product type', 'equals', 'Cleaners'),
    ]),
    ('clubs', 'Clubs', 'all conditions', [
        ('Product type', 'equals', 'Clubs'),
    ]),
    ('padel', 'Padel', 'all conditions', [
        ('Product tag', 'equals', 'Padel'),
    ]),
    ('pickleball', 'Pickleball', 'all conditions', [
        ('Product tag', 'equals', 'Pickleball'),
    ]),
    ('promo-special', 'Promo Special', 'all conditions', [
        ('Product tag', 'equals', 'Promo special'),
    ]),
    ('liquidations-football', 'Liquidations Football', 'all conditions', [
        ('Product tag', 'equals', 'Liquidations Football'),
    ]),

    # --- Clothing subcategories ---
    ('polos', 'Polos', 'all conditions', [
        ('Product type', 'equals', 'Clothing'),
        ('Product tag', 'equals', 'polos'),
    ]),
    ('shorts', 'Shorts', 'all conditions', [
        ('Product type', 'equals', 'Clothing'),
        ('Product tag', 'equals', 'shorts'),
    ]),
    ('t-shirts', 'T-Shirts', 'all conditions', [
        ('Product type', 'equals', 'Clothing'),
        ('Product tag', 'equals', 't-shirts'),
    ]),
    ('jackets', 'Jackets', 'all conditions', [
        ('Product type', 'equals', 'Clothing'),
        ('Product tag', 'equals', 'jackets'),
    ]),
    ('socks', 'Socks', 'all conditions', [
        ('Product type', 'equals', 'Clothing'),
        ('Product tag', 'equals', 'socks'),
    ]),
    ('suits', 'Suits', 'all conditions', [
        ('Product type', 'equals', 'Clothing'),
        ('Product tag', 'equals', 'suits'),
    ]),
    ('sweater', 'Sweater', 'all conditions', [
        ('Product type', 'equals', 'Clothing'),
        ('Product tag', 'equals', 'sweater'),
    ]),

    # --- Luggages subcategories ---
    ('bags', 'Bags', 'all conditions', [
        ('Product type', 'equals', 'Bags'),
        ('Product tag', 'equals', 'bags'),
    ]),
    ('batcover', 'Bat Covers', 'all conditions', [
        ('Product type', 'equals', 'Bags'),
        ('Product tag', 'equals', 'batcover'),
    ]),

    # --- Tables & Nets subcategories ---
    ('tables', 'Tables', 'all conditions', [
        ('Product type', 'equals', 'Tables and Nets'),
        ('Product tag', 'equals', 'tables'),
    ]),
    ('nets', 'Nets', 'all conditions', [
        ('Product type', 'equals', 'Tables and Nets'),
        ('Product tag', 'equals', 'nets'),
    ]),

    # --- Cleaners subcategories ---
    ('cleaners', 'Cleaners', 'all conditions', [
        ('Product type', 'equals', 'Cleaners'),
        ('Product tag', 'equals', 'cleaners'),
    ]),
    ('glue', 'Glue', 'all conditions', [
        ('Product type', 'equals', 'Cleaners'),
        ('Product tag', 'equals', 'glue'),
    ]),

    # --- Rubbers subcategories ---
    ('colours-rubbers', 'Coloured Rubbers', 'all conditions', [
        ('Product type', 'equals', 'Rubbers'),
        ('Product tag', 'equals', 'colours-rubbers'),
    ]),

    # --- Robots subcategories ---
    ('robots-machines', 'Robots', 'all conditions', [
        ('Product type', 'equals', 'Robots'),
        ('Product tag', 'equals', 'robots-machines'),
    ]),
    ('robots-accessories', 'Robot Accessories', 'all conditions', [
        ('Product type', 'equals', 'Robots'),
        ('Product tag', 'equals', 'robots-accessories'),
    ]),

    # --- Accessories subcategories ---
    ('accessories-rackets', 'Racket Accessories', 'all conditions', [
        ('Product type', 'equals', 'Accessories'),
        ('Product tag', 'equals', 'accessories-rackets'),
    ]),
    ('accessories-textiles', 'Textile Accessories', 'all conditions', [
        ('Product type', 'equals', 'Accessories'),
        ('Product tag', 'equals', 'accessories-textiles'),
    ]),

    # --- Football subcategories ---
    ('football-maillot', 'Football Jerseys', 'all conditions', [
        ('Product tag', 'equals', 'Liquidations Football'),
        ('Product tag', 'equals', 'football-maillot'),
    ]),
    ('football-short', 'Football Shorts', 'all conditions', [
        ('Product tag', 'equals', 'Liquidations Football'),
        ('Product tag', 'equals', 'football-short'),
    ]),
    ('football-bas', 'Football Socks', 'all conditions', [
        ('Product tag', 'equals', 'Liquidations Football'),
        ('Product tag', 'equals', 'football-bas'),
    ]),
]


def main():
    rows_written = 0

    with open(OUTPUT, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=COLS)
        writer.writeheader()

        for handle, title, must_match, rules in COLLECTIONS:
            for i, (col, rel, cond) in enumerate(rules):
                row = {c: '' for c in COLS}
                row['Handle'] = handle
                row['Rule: Column'] = col
                row['Rule: Relation'] = rel
                row['Rule: Condition'] = cond

                if i == 0:
                    row['Command'] = 'MERGE'
                    row['Title'] = title
                    row['Published'] = 'true'
                    row['Sort Order'] = 'best-selling'
                    row['Must Match'] = must_match

                writer.writerow(row)
                rows_written += 1

    top_level = sum(1 for _, _, _, r in COLLECTIONS if len(r) == 1)
    sub_level = sum(1 for _, _, _, r in COLLECTIONS if len(r) > 1)

    print(f"Done.")
    print(f"  Collections: {len(COLLECTIONS)} ({top_level} top-level + {sub_level} sub)")
    print(f"  CSV rows: {rows_written}")
    print(f"  Output → {OUTPUT}")


if __name__ == '__main__':
    main()
