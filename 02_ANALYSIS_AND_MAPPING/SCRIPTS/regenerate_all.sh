#!/bin/bash
# Régénère tous les fichiers d'import Shopify + fichiers de purge
# À lancer après mise à jour de 01_DATA_RAW/export_magento_products_all.csv

set -e
DIR="$(cd "$(dirname "$0")/../.." && pwd)"
SCRIPTS="$DIR/02_ANALYSIS_AND_MAPPING/SCRIPTS"

echo "=== Régénération complète ==="
echo "Source: $DIR/01_DATA_RAW/export_magento_products_all.csv"
echo ""

echo "[1/8] Produits + traductions..."
python3 "$SCRIPTS/magento_to_shopify.py"
echo ""

echo "[2/8] Collections..."
python3 "$SCRIPTS/generate_collections.py"
echo ""

echo "[3/8] Redirections..."
python3 "$SCRIPTS/generate_redirects.py"
echo ""

echo "[4/8] Customers..."
python3 "$SCRIPTS/magento_to_shopify_customers.py"
echo ""

echo "[5/8] Commandes 2025-2026..."
python3 "$SCRIPTS/magento_to_shopify_orders.py"
echo ""

echo "[6/8] Sample (produits, clients, commandes — par boutique)..."
python3 - << 'SAMPLEEOF'
import csv, os

base = os.environ.get('DIR', '.')
imports = os.path.join(base, '04_SHOPIFY_IMPORTS')

targets = [
    ('Blades', 'Handle', None), ('Rubbers', 'Color', 'Thickness'),
    ('Clothing', 'Size', None), ('Shoes', 'Size', None),
    ('Bags', 'Color', None), ('Balls', 'Quantity', None),
    ('Cleaners', 'Quantity', None), ('Tables and Nets', 'Color', None),
    ('Accessories', 'Title', None), ('Blades', 'Title', None),
]

def build_products_sample(store_suffix):
    src = os.path.join(imports, f'shopify_products_{store_suffix}.csv')
    with open(src, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        all_rows = list(reader)
        fieldnames = reader.fieldnames

    handles, seen = [], set()
    for want_type, want_o1, want_o2 in targets:
        for r in all_rows:
            if not r.get('Title') or r['Handle'] in seen:
                continue
            if r.get('Type') == want_type and r.get('Option1 Name') == want_o1:
                if want_o2 is None or r.get('Option2 Name') == want_o2:
                    seen.add(r['Handle'])
                    handles.append(r['Handle'])
                    break

    sample = [r for r in all_rows if r['Handle'] in handles]
    dest = os.path.join(imports, f'shopify_products_sample_{store_suffix}.csv')
    with open(dest, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(sample)
    print(f"  {store_suffix}: {len(handles)} produits, {len(sample)} lignes")


def build_customers_sample(store_suffix, n=10):
    src = os.path.join(imports, f'shopify_customers_{store_suffix}.csv')
    with open(src, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        all_rows = list(reader)
        fieldnames = reader.fieldnames

    with_addr = [r for r in all_rows if r.get('Address1')]
    without_addr = [r for r in all_rows if not r.get('Address1')]
    half = n // 2
    sample = with_addr[:half] + without_addr[:n - half]
    if len(sample) < n:
        rest = [r for r in all_rows if r not in sample]
        sample += rest[:n - len(sample)]

    dest = os.path.join(imports, f'shopify_customers_sample_{store_suffix}.csv')
    with open(dest, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(sample)
    print(f"  {store_suffix}: {len(sample)} clients")


def build_orders_sample(store_suffix, n=5):
    src = os.path.join(imports, f'shopify_orders_{store_suffix}.csv')
    with open(src, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        all_rows = list(reader)
        fieldnames = reader.fieldnames

    order_names, seen = [], set()
    for r in all_rows:
        name = r.get('Name', '')
        if name and name not in seen:
            seen.add(name)
            order_names.append(name)
        if len(order_names) >= n:
            break

    wanted = set(order_names)
    sample = [r for r in all_rows if r.get('Name') in wanted]
    dest = os.path.join(imports, f'shopify_orders_sample_{store_suffix}.csv')
    with open(dest, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(sample)
    print(f"  {store_suffix}: {len(order_names)} commandes, {len(sample)} lignes")


print("Produits :")
build_products_sample('dandoy')
build_products_sample('butterfly')
print("Clients :")
build_customers_sample('dandoy')
build_customers_sample('butterfly')
print("Commandes :")
build_orders_sample('dandoy')
build_orders_sample('butterfly')
SAMPLEEOF
echo ""

echo "[7/8] Fichiers de purge (par boutique)..."
python3 - << 'PYEOF'
import csv, os

base = os.environ.get('DIR', '.')
imports = os.path.join(base, '04_SHOPIFY_IMPORTS')
redirects_dir = os.path.join(base, '03_SEO_AND_REDIRECTS')

def purge_handles(src_path, dest_path):
    handles, seen = [], set()
    with open(src_path, encoding='utf-8') as f:
        for row in csv.DictReader(f):
            h = row.get('Handle', '')
            if h and h not in seen:
                seen.add(h)
                handles.append(h)
    with open(dest_path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['Command', 'Handle'])
        w.writeheader()
        for h in handles:
            w.writerow({'Command': 'DELETE', 'Handle': h})
    return len(handles)

def purge_redirects(src_path, dest_path):
    with open(src_path, encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    with open(dest_path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['Command', 'Redirect From', 'Redirect To'])
        w.writeheader()
        for r in rows:
            w.writerow({'Command': 'DELETE', 'Redirect From': r['Redirect From'], 'Redirect To': r['Redirect To']})
    return len(rows)

# Orders imported through the Shopify API (as Matrixify does) are eligible
# for bulk DELETE regardless of fulfillment status — unlike bulk CANCEL,
# which Matrixify blocks once an order is fulfilled. Filename must contain
# "Order" for Matrixify to route it to the Orders importer.
def purge_orders(src_path, dest_path):
    names, seen = [], set()
    with open(src_path, encoding='utf-8') as f:
        for row in csv.DictReader(f):
            n = row.get('Name', '')
            if n and n not in seen:
                seen.add(n)
                names.append(n)
    with open(dest_path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['Command', 'Name'])
        w.writeheader()
        for n in names:
            w.writerow({'Command': 'DELETE', 'Name': n})
    return len(names)

for suffix in ('dandoy', 'butterfly'):
    n_products = purge_handles(
        os.path.join(imports, f'shopify_products_{suffix}.csv'),
        os.path.join(imports, f'shopify_products_{suffix}_PURGE.csv'))
    n_collections = purge_handles(
        os.path.join(imports, f'shopify_collections_{suffix}.csv'),
        os.path.join(imports, f'shopify_collections_{suffix}_PURGE.csv'))
    n_redirects = purge_redirects(
        os.path.join(redirects_dir, f'shopify_redirects_{suffix}.csv'),
        os.path.join(imports, f'shopify_redirects_{suffix}_PURGE.csv'))
    n_orders = purge_orders(
        os.path.join(imports, f'shopify_orders_{suffix}.csv'),
        os.path.join(imports, f'shopify_orders_{suffix}_PURGE.csv'))
    print(f"  {suffix}: {n_products} produits, {n_collections} collections, {n_redirects} redirections, {n_orders} commandes")
PYEOF

echo ""
echo "[8/8] Validation..."
set +e
python3 "$SCRIPTS/validate_shopify_csv.py"
VALIDATION_EXIT=$?
set -e

echo ""
echo "=== Terminé ==="
echo "Fichiers dans 04_SHOPIFY_IMPORTS/ et 03_SEO_AND_REDIRECTS/"
if [ "$VALIDATION_EXIT" -ne 0 ]; then
    echo ""
    echo "⚠ La validation a détecté des erreurs bloquantes — voir le détail ci-dessus avant tout import Matrixify."
fi
exit "$VALIDATION_EXIT"
