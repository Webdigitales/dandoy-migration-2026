# Guide Projet : Migration Magento vers Shopify (Dandoy-Sports)

Ce fichier centralise le contexte, les contraintes techniques et les directives de développement pour assister l'équipe et les agents IA (Claude Code) dans la migration de l'écosystème Dandoy-Sports & Butterfly.

---

## 1. Contexte & Périmètre du Projet

- **Client :** Dandoy-Sports / Butterfly TT
- **Objectif :** Migration complète de Magento 2 vers Shopify (instance unique + Shopify Markets — Option A retenue).
- **Périmètre Multi-sites (6 Domaines/Sous-domaines) :**
  - `dandoy-sports.com` (Principal)
  - `fr.dandoy-sports.eu`, `en.dandoy-sports.eu`, `nl.dandoy-sports.eu`
  - `be.butterfly.tt`, `nl.butterfly.tt` (Identité de marque stricte)
- **Outil d'import :** Matrixify (plan Enterprise requis — 41k clients + 125k commandes)
- **Documentation :** Site MkDocs déployé via GitHub Pages (`05_DOCS/`)

---

## 2. Contraintes Techniques Majeures (⚠️ À respecter scrupuleusement)

### A. Gestion des Stocks (Pas d'ERP)
- **Fonctionnement :** Une application sur mesure (sans API) génère un export CSV **1x par jour**.
- **Liaison obligatoire :** La synchronisation se fait au caractère près via le **SKU**. Interdiction stricte de modifier la structure des SKUs existants lors du mapping de données.
- **Outil cible :** Application Shopify *Stock Sync* connectée à un serveur SFTP sécurisé.

### B. Erreur d'Les commandes sont liéArchitecture Catalogue (Grouped Products)
- **Le Problème :** Sur Magento, les produits à variantes ont été configurés en *Grouped Products* au lieu de Configurable Products.
- **La Solution :** Le script `magento_to_shopify.py` restructure la donnée :
  - `url_key` du parent → **Handle** Shopify
  - Produits simples enfants → **Variantes** Shopify
  - `additional_attributes` (ex: `baldes_handles=handle-ANATOMIC`) → options natives Shopify
- **Résultat :** 25 514 lignes CSV (4 834 produits, 6 723 traductions)

### C. Limites Natives de Shopify
- **Plafond des 100 variantes :** Audité — maximum constaté = 33 variantes (textiles Joola). Pas de scission nécessaire.
- **Options vides :** Shopify refuse les options déclarées sans valeur. Le script omet les options vides automatiquement.

### D. Variant Images — Décision actuelle : non activé
Les variant images ne sont PAS exportées pour éviter le doublon dans la galerie produit.
Pour réactiver : voir section 6 de `05_DOCS/contraintes-techniques.md`.

### E. Metafields
- 19 metafields custom créés par Matrixify à l'import.
- Types : `single_line_text_field` (simple) ou `list.single_line_text_field` (multi-valeurs avec pipe `|`).
- `promotion_type` et `shoe_type` sont en `list` (multi-valeurs).
- Choix prédéfinis configurés pour 15 metafields dans Shopify Admin.
- `custom.technology` : texte libre (77 valeurs, pas de dropdown).

---

## 3. Structure du Dossier de Travail

```text
dandoy/
├── 01_DATA_RAW/                    # Exports bruts Magento (gitignorés)
│   ├── export_magento_products_all.csv
│   ├── export_customer.csv
│   ├── export_customer_address.csv
│   └── export_order_all_2025_2026.csv
│
├── 02_ANALYSIS_AND_MAPPING/
│   ├── SCRIPTS/
│   │   ├── magento_to_shopify.py           ← script principal (produits + traductions)
│   │   ├── generate_redirects.py           ← redirections 301
│   │   ├── generate_collections.py         ← smart collections
│   │   ├── magento_to_shopify_customers.py ← conversion clients
│   │   ├── magento_to_shopify_orders.py    ← conversion commandes 2025-2026
│   │   └── regenerate_all.sh               ← tout régénérer (7 étapes)
│   ├── matrice_data_mapping_products.md
│   └── avancement_migration.md
│
├── 03_SEO_AND_REDIRECTS/
│   └── shopify_redirects.csv               (2 368 redirections, gitignorés)
│
├── 04_SHOPIFY_IMPORTS/                     # CSV prêts à l'import (gitignorés sauf sample)
│   ├── shopify_products.csv                (25 514 lignes — 4 834 produits)
│   ├── shopify_translations.csv            (6 723 lignes)
│   ├── shopify_collections.csv             (37 collections)
│   ├── shopify_customers.csv               (41 020 clients dédupliqués)
│   ├── shopify_products_sample.csv         (10 produits — versionné)
│   └── *_PURGE.csv (×3)
│
└── 05_DOCS/                                # Source MkDocs (GitHub Pages)
    ├── index.md, quick-start.md, contraintes-techniques.md, avancement.md
    ├── mapping/   (matrice, metafields ×3, custom-options, bundles)
    ├── architecture/  (multi-sites, langues)
    ├── import/    (matrixify, redirections, customers, orders)
    └── stock/     (guide prestataire)
```

---

## 4. Scripts & Régénération

### Régénérer tous les fichiers d'import

```bash
bash 02_ANALYSIS_AND_MAPPING/SCRIPTS/regenerate_all.sh
```

7 étapes : [1/7] produits + traductions → [2/7] collections → [3/7] redirections → [4/7] customers → [5/7] commandes → [6/7] sample → [7/7] purge.

### Ordre d'import Matrixify recommandé

1. `shopify_products_sample.csv` (test — 10 produits)
2. `shopify_products.csv`
3. `shopify_collections.csv`
4. `shopify_customers.csv`
5. Activer FR + NL dans Settings → Languages
6. `shopify_translations.csv`
7. `shopify_redirects.csv`

---

## 5. Données Migrées

| Entité | Fichier source | Résultat |
|---|---|---|
| Produits | `export_magento_products_all.csv` | 4 834 produits, 25 514 lignes CSV |
| Traductions | Idem (store views fr/nl) | 6 723 lignes (93% FR, 71% NL) |
| Collections | Généré depuis tags | 37 smart collections |
| Redirections | Crawl HTTP live | 2 368 redirections 301 |
| Clients | `export_customer.csv` + adresses | 41 020 (dédupliqués depuis 46 423) |
| Commandes | `export_order_all_2025_2026.csv` | 37 430 commandes 2025-2026 avec line items → `shopify_orders.csv` (99 821 lignes) |

---

## 6. Décisions en Attente

| Sujet | Options | Recommandation |
|---|---|---|
| **Multi-sites** | A : instance unique / B : deux boutiques | **Option A** recommandée |
| **Migration commandes** | Import 2025-2026 avec line items | `shopify_orders.csv` prêt — 37 430 commandes |
| **Custom options** | Line item properties (natif) | Retenu — code thème à ajouter |
| **Livraison tables** (33 produits) | App tierce | Retenu — prix variables 41–116 € |

---

## 7. Directives de Développement

- Ne jamais modifier la structure des SKUs
- Les options Shopify vides sont omises (ne pas déclarer `Option Name` sans `Option Value`)
- Metafields multi-valeurs : séparer par `|` (pipe), type `list.single_line_text_field`
- Les CSV générés sont gitignorés (sauf `shopify_products_sample.csv`)
- Toute nouvelle documentation va dans `05_DOCS/` et est référencée dans `mkdocs.yml`
- Le site MkDocs se déploie automatiquement via GitHub Actions sur push `master`
