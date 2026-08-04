# Guide Projet : Migration Magento vers Shopify (Dandoy-Sports)

Ce fichier centralise le contexte, les contraintes techniques et les directives de développement pour assister l'équipe et les agents IA (Claude Code) dans la migration de l'écosystème Dandoy-Sports & Butterfly.

---

## 1. Contexte & Périmètre du Projet

- **Client :** Dandoy-Sports / Butterfly TT
- **Objectif :** Migration complète de Magento 2 vers Shopify — **deux boutiques Shopify séparées (Option B, décidée le 29 juillet 2026)** : une instance complète pour Dandoy-Sports, une instance en plan **Basic** pour Butterfly TT.
- **Périmètre Multi-sites (6 Domaines/Sous-domaines, répartis sur 2 boutiques) :**
  - **Boutique Dandoy-Sports** : `dandoy-sports.com` (hors Union Européenne / international), `fr.dandoy-sports.eu`, `en.dandoy-sports.eu`, `nl.dandoy-sports.eu` (Dandoy EU) — Shopify Markets gère en interne la distinction hors-UE / UE (TVA différente)
  - **Boutique Butterfly TT** (plan Basic) : `be.butterfly.tt`, `nl.butterfly.tt` (Identité de marque stricte)
  - **199 produits partagés entre les deux marques (35 actifs)** : dupliqués manuellement dans les deux catalogues, tagués `dandoy` + `butterfly` dans les deux — double maintenance acceptée par le client, ainsi que le risque de survente sur ces produits (stock sync 1×/jour, deux boutiques distinctes)
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
- **Résultat :** 4 834 produits uniques (dont 199 partagés Dandoy/Butterfly), répartis en deux CSV par boutique (Option B — voir section 5) — 27 128 lignes produits et 7 001 lignes traductions au total

### C. Limites Natives de Shopify
- **Plafond des 100 variantes :** Audité — maximum constaté = 33 variantes (textiles Joola). Pas de scission nécessaire.
- **Options vides :** Shopify refuse les options déclarées sans valeur. Le script omet les options vides automatiquement.

### D. Variant Images — Décision actuelle : non activé
Les variant images ne sont PAS exportées pour éviter le doublon dans la galerie produit.
Pour réactiver : voir section 6 de `05_DOCS/contraintes-techniques.md`.

### E. Metafields
- 20 metafields custom créés par Matrixify à l'import.
- Types : `single_line_text_field` (simple) ou `list.single_line_text_field` (multi-valeurs, séparateur `;` dans le CSV généré).
- `promotion_type`, `shoe_type` et `available_options` (Gluing/EdgeTape/Lacquering — voir section 7 et `05_DOCS/mapping/custom-options.md`) sont en `list` (multi-valeurs).
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
│   │   ├── validate_shopify_csv.py         ← validation post-régénération (SKU, options, handles)
│   │   └── regenerate_all.sh               ← tout régénérer (8 étapes)
│   ├── matrice_data_mapping_products.md
│   └── avancement_migration.md
│
├── 03_SEO_AND_REDIRECTS/
│   ├── shopify_redirects_dandoy.csv        (2 045 redirections, gitignoré)
│   └── shopify_redirects_butterfly.csv     (380 redirections, gitignoré)
│
├── 04_SHOPIFY_IMPORTS/                     # CSV prêts à l'import (gitignorés sauf sample), 1 jeu par boutique
│   ├── shopify_products_dandoy.csv         (22 223 lignes — 4 183 produits)
│   ├── shopify_products_butterfly.csv      (4 905 lignes — 849 produits)
│   ├── shopify_translations_dandoy.csv     (5 768 lignes)
│   ├── shopify_translations_butterfly.csv  (1 233 lignes)
│   ├── shopify_collections_dandoy.csv      (37 collections, 58 lignes)
│   ├── shopify_collections_butterfly.csv   (37 collections, 58 lignes)
│   ├── shopify_customers_dandoy.csv        (33 357 clients)
│   ├── shopify_customers_butterfly.csv     (11 404 clients)
│   ├── shopify_orders_dandoy.csv           (71 096 lignes — 23 823 commandes)
│   ├── shopify_orders_butterfly.csv        (28 725 lignes — 13 607 commandes)
│   ├── shopify_products_sample_dandoy.csv     (versionné)
│   ├── shopify_products_sample_butterfly.csv  (versionné)
│   ├── shopify_customers_sample_dandoy.csv    (versionné — 10 clients)
│   ├── shopify_customers_sample_butterfly.csv (versionné — 10 clients)
│   ├── shopify_orders_sample_dandoy.csv       (versionné — 5 commandes)
│   ├── shopify_orders_sample_butterfly.csv    (versionné — 5 commandes)
│   └── *_PURGE.csv (×8 — produits/collections/redirections/commandes × 2 boutiques)
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

8 étapes : [1/8] produits + traductions → [2/8] collections → [3/8] redirections → [4/8] customers → [5/8] commandes → [6/8] sample → [7/8] purge → [8/8] validation.

La validation (`validate_shopify_csv.py`) rejoue en local les règles qui font échouer un import Matrixify : SKU dupliqués entre produits (risque pour Stock Sync — voir section 2.A), combinaisons de variantes dupliquées ou options incohérentes au sein d'un produit, plafond des 100 variantes, prix manquant/négatif, et handles orphelins dans les traductions/redirections. Le script sort en erreur (code 1) si des problèmes bloquants sont trouvés, sans empêcher la génération des autres fichiers. Les avertissements (ex. Vendor vide) n'affectent pas le code de sortie.

### Ordre d'import Matrixify recommandé (à répéter dans chacune des deux boutiques)

1. `shopify_products_sample_{dandoy|butterfly}.csv` (test — quelques produits)
2. `shopify_products_{dandoy|butterfly}.csv`
3. `shopify_collections_{dandoy|butterfly}.csv`
4. `shopify_customers_{dandoy|butterfly}.csv`
5. Activer FR + NL (+ EN pour Dandoy) dans Settings → Languages
6. `shopify_translations_{dandoy|butterfly}.csv`
7. `shopify_redirects_{dandoy|butterfly}.csv`

> Les 199 produits partagés (35 actifs) sont présents dans les deux fichiers `shopify_products_*.csv`, tagués `dandoy,butterfly` — à importer normalement dans chaque boutique, aucune étape manuelle supplémentaire.

---

## 5. Données Migrées

Chaque entité est scindée en deux fichiers, un par boutique (produits partagés dupliqués dans les deux).

| Entité | Fichier source | Dandoy-Sports | Butterfly TT |
|---|---|---|---|
| Produits | `export_magento_products_all.csv` | 4 183 produits, 22 223 lignes CSV | 849 produits, 4 905 lignes CSV |
| Traductions | Idem (store views fr/nl) | 5 768 lignes (FR 3 856, NL 3 417) | 1 233 lignes (FR 809, NL 19) |
| Collections | Généré depuis tags | 37 smart collections | 37 smart collections |
| Redirections | Crawl HTTP live | 2 045 redirections 301 | 380 redirections 301 |
| Clients | `export_customer.csv` + adresses | 33 357 (dédupliqués, dont partagés) | 11 404 (dédupliqués, dont partagés) |
| Commandes | `export_order_all_2025_2026.csv` | 23 823 commandes → `shopify_orders_dandoy.csv` (71 096 lignes) | 13 607 commandes → `shopify_orders_butterfly.csv` (28 725 lignes) |

> 4 834 produits uniques au total (dont 199 partagés, 35 actifs) et 41 020 clients uniques au total (dont les partagés dupliqués entre les deux fichiers ci-dessus).

---

## 6. Décisions en Attente

| Sujet | Options | Décision |
|---|---|---|
| **Multi-sites** | A : instance unique / B : deux boutiques | **Option B retenue (29 juillet 2026)** : deux boutiques séparées, Butterfly en plan Basic |
| **Migration commandes** | Import 2025-2026 avec line items | Prêt, scindé par boutique — voir section 5 |
| **Custom options** | Line item properties (natif) | Retenu — code thème à ajouter |
| **Livraison tables** (33 produits) | App tierce | Retenu — prix variables 41–116 € |
| **Plan Basic Butterfly** | Limitations à valider (rapports, shipping tiers calculé, comptes staff) | À vérifier avant validation finale |

---

## 7. Directives de Développement

- Ne jamais modifier la structure des SKUs
- Les options Shopify vides sont omises (ne pas déclarer `Option Name` sans `Option Value`)
- Metafields multi-valeurs : séparer par `|` (pipe), type `list.single_line_text_field`
- Les CSV générés sont gitignorés (sauf les 6 fichiers `*_sample_{dandoy|butterfly}.csv` : produits, clients, commandes)
- Toute nouvelle documentation va dans `05_DOCS/` et est référencée dans `mkdocs.yml`
- Le site MkDocs se déploie automatiquement via GitHub Actions sur push `master`
- **Deux boutiques Shopify (Option B)** : tout script de génération doit produire une paire de fichiers `_dandoy` / `_butterfly` (voir `brand_scope()` dans `magento_to_shopify.py`, basé sur `product_websites`). Les produits partagés (tag `dandoy,butterfly`) sont dupliqués volontairement dans les deux fichiers produits — ne pas les dédupliquer.
