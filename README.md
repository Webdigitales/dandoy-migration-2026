# Migration Dandoy-Sports → Shopify

Migration Magento 2 vers Shopify pour **Dandoy-Sports / Butterfly TT** (6 domaines, 3 langues,
**deux boutiques Shopify séparées** — Option B, décidée le 29 juillet 2026).

📖 **Documentation complète :** [webdigitales.github.io/dandoy-migration-2026](https://webdigitales.github.io/dandoy-migration-2026/)

---

## Fichiers d'import Shopify

Un jeu de fichiers par boutique — les 199 produits partagés entre les deux marques sont
dupliqués dans les deux jeux (voir [Multi-sites](https://webdigitales.github.io/dandoy-migration-2026/architecture/multi-sites/)).

| Fichier | Contenu | Dandoy-Sports | Butterfly TT |
|---|---|---|---|
| `shopify_products_{store}.csv` | Produits EN + 20 metafields + tags | 22 223 lignes | 4 905 lignes |
| `shopify_translations_{store}.csv` | Traductions FR + NL | 5 768 lignes | 1 233 lignes |
| `shopify_collections_{store}.csv` | 37 smart collections | 58 lignes | 58 lignes |
| `shopify_redirects_{store}.csv` | Redirections 301 | 2 045 lignes | 380 lignes |
| `shopify_customers_{store}.csv` | Clients dédupliqués | 33 357 | 11 404 |
| `shopify_orders_{store}.csv` | Commandes 2025-2026 | 71 096 lignes | 28 725 lignes |

## Régénérer les fichiers

Après mise à jour de l'export Magento (`01_DATA_RAW/export_magento_products_all.csv`) :

```bash
# Tout régénérer pour les 2 boutiques (produits, traductions, collections, redirections,
# clients, commandes, sample, fichiers de purge)
bash 02_ANALYSIS_AND_MAPPING/SCRIPTS/regenerate_all.sh
```

Ou individuellement (chaque script génère les fichiers `_dandoy` et `_butterfly` en une seule exécution) :

```bash
python3 02_ANALYSIS_AND_MAPPING/SCRIPTS/magento_to_shopify.py            # Produits + traductions
python3 02_ANALYSIS_AND_MAPPING/SCRIPTS/generate_collections.py          # Collections
python3 02_ANALYSIS_AND_MAPPING/SCRIPTS/generate_redirects.py            # Redirections 301
python3 02_ANALYSIS_AND_MAPPING/SCRIPTS/magento_to_shopify_customers.py  # Clients
python3 02_ANALYSIS_AND_MAPPING/SCRIPTS/magento_to_shopify_orders.py     # Commandes
```

## Structure

```
├── 01_DATA_RAW/                    Export brut Magento
├── 02_ANALYSIS_AND_MAPPING/
│   ├── SCRIPTS/                    Scripts de conversion Python
│   └── *.md                        Documentation technique
├── 03_SEO_AND_REDIRECTS/           Redirections 301
├── 04_SHOPIFY_IMPORTS/             Fichiers prêts pour Matrixify
└── 05_DOCS/                        Source du site MkDocs
```
