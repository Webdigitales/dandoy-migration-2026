#!/bin/bash
# Régénère tous les fichiers d'import Shopify + fichiers de purge
# À lancer après mise à jour de 01_DATA_RAW/export_magento_products_all.csv

set -e
DIR="$(cd "$(dirname "$0")/../.." && pwd)"
SCRIPTS="$DIR/02_ANALYSIS_AND_MAPPING/SCRIPTS"

echo "=== Régénération complète ==="
echo "Source: $DIR/01_DATA_RAW/export_magento_products_all.csv"
echo ""

echo "[1/3] Produits + traductions..."
python3 "$SCRIPTS/magento_to_shopify.py"
echo ""

echo "[2/3] Collections..."
python3 "$SCRIPTS/generate_collections.py"
echo ""

echo "[3/3] Redirections..."
python3 "$SCRIPTS/generate_redirects.py"
echo ""

echo "[4/4] Fichiers de purge..."
python3 - << 'PYEOF'
import csv, os

base = os.environ.get('DIR', '.')
imports = os.path.join(base, '04_SHOPIFY_IMPORTS')

# Purge produits
handles = []
seen = set()
with open(os.path.join(imports, 'shopify_products.csv'), encoding='utf-8') as f:
    for row in csv.DictReader(f):
        h = row.get('Handle', '')
        if h and h not in seen:
            seen.add(h)
            handles.append(h)
with open(os.path.join(imports, 'shopify_products_PURGE.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=['Command', 'Handle'])
    w.writeheader()
    for h in handles:
        w.writerow({'Command': 'DELETE', 'Handle': h})

# Purge collections
handles_c = []
seen_c = set()
with open(os.path.join(imports, 'shopify_collections.csv'), encoding='utf-8') as f:
    for row in csv.DictReader(f):
        h = row.get('Handle', '')
        if h and h not in seen_c:
            seen_c.add(h)
            handles_c.append(h)
with open(os.path.join(imports, 'shopify_collections_PURGE.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=['Command', 'Handle'])
    w.writeheader()
    for h in handles_c:
        w.writerow({'Command': 'DELETE', 'Handle': h})

# Purge redirections
redirects_path = os.path.join(base, '03_SEO_AND_REDIRECTS', 'shopify_redirects.csv')
with open(redirects_path, encoding='utf-8') as f:
    rows = list(csv.DictReader(f))
with open(os.path.join(imports, 'shopify_redirects_PURGE.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=['Command', 'Redirect From', 'Redirect To'])
    w.writeheader()
    for r in rows:
        w.writerow({'Command': 'DELETE', 'Redirect From': r['Redirect From'], 'Redirect To': r['Redirect To']})

print(f"  Purge: {len(handles)} produits, {len(handles_c)} collections, {len(rows)} redirections")
PYEOF

echo ""
echo "=== Terminé ==="
echo "Fichiers dans 04_SHOPIFY_IMPORTS/ et 03_SEO_AND_REDIRECTS/"
