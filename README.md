# Migration Dandoy-Sports → Shopify

Migration Magento 2 vers Shopify pour **Dandoy-Sports / Butterfly TT** (6 domaines, 3 langues).

📖 **Documentation complète :** [webdigitales.github.io/dandoy-migration-2026](https://webdigitales.github.io/dandoy-migration-2026/)

---

## Fichiers d'import Shopify

| Fichier | Contenu | Lignes |
|---|---|---|
| `shopify_products.csv` | 4 834 produits EN + 19 metafields + tags | 25 514 |
| `shopify_translations.csv` | Traductions FR (93%) + NL (71%) | 6 723 |
| `shopify_collections.csv` | 37 smart collections | 58 |
| `shopify_redirects.csv` | Redirections 301 | 2 368 |

## Régénérer les fichiers

```bash
# Produits + traductions
python3 02_ANALYSIS_AND_MAPPING/SCRIPTS/magento_to_shopify.py

# Collections
python3 02_ANALYSIS_AND_MAPPING/SCRIPTS/generate_collections.py

# Redirections 301
python3 02_ANALYSIS_AND_MAPPING/SCRIPTS/generate_redirects.py
```

Source : `01_DATA_RAW/export_magento_products_all.csv`

## Structure

```
├── 01_DATA_RAW/                    Export brut Magento
├── 02_ANALYSIS_AND_MAPPING/
│   ├── SCRIPTS/                    Scripts de conversion Python
│   └── *.md                        Documentation technique
├── 03_SEO_AND_REDIRECTS/           Redirections 301
├── 04_SHOPIFY_IMPORTS/             Fichiers prêts pour Matrixify
└── docs/                           Source du site MkDocs
```
