# Avancement Migration Magento → Shopify — Dandoy-Sports / Butterfly TT

Dernière mise à jour : **26 juin 2026**

---

## Arborescence du projet

```
dandoy/
├── 01_DATA_RAW/                                 (gitignorés)
│   ├── export_magento_products_all.csv          (91 Mo)
│   ├── export_customer.csv
│   ├── export_customer_address.csv
│   └── export_order_all_2025_2026.csv
├── 02_ANALYSIS_AND_MAPPING/
│   ├── SCRIPTS/
│   │   ├── magento_to_shopify.py                ← produits + traductions
│   │   ├── generate_collections.py              ← smart collections
│   │   ├── generate_redirects.py                ← redirections 301
│   │   ├── magento_to_shopify_customers.py      ← clients
│   │   ├── magento_to_shopify_orders.py         ← commandes 2025-2026
│   │   └── regenerate_all.sh                    ← tout régénérer (7 étapes)
│   ├── SCREENSHOTS_CATALOGUE/                   (8 captures Magento)
│   ├── plan-matrixify.png
│   ├── matrice_data_mapping_products.md
│   ├── metafields_shopify.md
│   ├── custom_options_shopify.md
│   ├── gestion_langues_shopify.md
│   ├── multi_sites_shopify.md
│   ├── bundles_shopify.md
│   ├── regles_import_matrixify.md
│   ├── trustpilot-widgets.md
│   └── avancement_migration.md
├── 03_SEO_AND_REDIRECTS/
│   ├── shopify_redirects.csv                    (gitignorés)
│   └── redirections_301.md
├── 04_SHOPIFY_IMPORTS/                          (CSV gitignorés sauf sample)
│   ├── shopify_products.csv                     (25 514 lignes)
│   ├── shopify_translations.csv                 (6 723 lignes)
│   ├── shopify_collections.csv                  (37 collections)
│   ├── shopify_customers.csv                    (41 020 clients)
│   ├── shopify_orders.csv                       (99 821 lignes — 37 430 commandes)
│   ├── shopify_products_sample.csv              (10 produits — versionné)
│   ├── *_PURGE.csv (×3)
│   └── ERRORS/                                  (rapports d'import Matrixify)
├── 05_DOCS/                                     (source MkDocs — GitHub Pages)
│   ├── index.md, quick-start.md, contraintes-techniques.md, avancement.md
│   ├── mapping/        (matrice, metafields ×3, custom-options, bundles)
│   ├── architecture/   (multi-sites, langues)
│   ├── import/         (plan-migration, matrixify, redirections, customers, orders)
│   └── stock/          (guide-prestataire)
├── CLAUDE.md, README.md, GUIDE_PRESTATAIRE.md
└── mkdocs.yml + .github/workflows/docs.yml
```

---

## Fichiers d'import Shopify prêts

| Fichier | Lignes | Contenu |
|---|---|---|
| `shopify_products.csv` | 25 514 | 4 834 produits EN + 19 metafields + 22 tags sous-catégories |
| `shopify_translations.csv` | 6 723 | Traductions FR (93% couvert) + NL (71% couvert) |
| `shopify_collections.csv` | 58 | 37 smart collections (16 top-level + 21 sous-catégories) |
| `shopify_redirects.csv` | 2 368 | Redirections 301 (produits actifs + catégories) |
| `shopify_customers.csv` | 41 020 | Clients dédupliqués + adresse par défaut + tags source |
| `*_PURGE.csv` (×3) | — | Fichiers de suppression Matrixify pour repartir à zéro entre tests |
| `shopify_products_sample.csv` | 53 | Échantillon 10 produits (tous types) |

### Ordre d'import recommandé

1. `shopify_products_sample.csv` — test avec 10 produits, vérifier, supprimer manuellement
2. `shopify_products.csv` — produits + variantes + metafields + tags
3. `shopify_collections.csv` — collections (auto-remplies via tags/types)
4. `shopify_customers.csv` — clients + adresses
5. Activer les langues FR et NL dans Settings → Languages
6. `shopify_translations.csv` — traductions FR/NL
7. `shopify_redirects.csv` — redirections 301

### Régénération

Après mise à jour de l'export Magento :

```bash
bash 02_ANALYSIS_AND_MAPPING/SCRIPTS/regenerate_all.sh
```

### Purge (pour repartir à zéro entre tests)

Importer via Matrixify dans l'ordre inverse :

1. `shopify_redirects_PURGE.csv`
2. `shopify_collections_PURGE.csv`
3. `shopify_products_PURGE.csv`

---

## Travaux réalisés

### Analyse des données (12–17 juin 2026)

- Export brut Magento : 417 838 lignes, 89 colonnes, 10 store views
- Identification des types : 76 175 simples, 11 742 grouped, 292 bundles, 8 gift cards
- Analyse des attribute sets : 14 types de produits
- Analyse des screenshots catalogue Magento (catégories + fiches produit)
- Audit limite 100 variantes : max constaté = 33, aucun dépassement

### Script de conversion (16–22 juin 2026)

- Conversion grouped products → produits Shopify avec variantes
- Mapping des options par type de produit :
  - Blades → Handle (Anatomic, Flared, Straight…)
  - Rubbers → Color + Thickness
  - Clothing → Size
  - Shoes → Size (sans préfixe EU)
  - Bags → Color
  - Balls → Quantity + Color (omis si vide)
  - Cleaners → Quantity
  - Tables and Nets → Color (depuis suffixe du nom)
  - Autres → fallback sur suffixe du nom
- 19 metafields custom (blade_category, pimples, hardness, technology, gender…)
- Export des traductions FR/NL depuis eu_fr, bt_be_fr, eu_nl
- Fix : options vides omises (erreur Matrixify Xushaofa Balls corrigée)
- Fix : promotion_type et shoe_type passés en list (multi-valeurs avec pipe)

### Collections Shopify (22 juin 2026)

- 22 tags de sous-catégories ajoutés aux produits
- 37 smart collections générées (16 top-level + 21 sous-catégories)
- Règles basées sur Product Type + Product Tag (remplissage automatique)

### Redirections 301 (22 juin 2026)

- Vérification HTTP sur le site Magento live : seuls les produits actifs et visibles redirigés
- Résultat : 2 368 redirections (au lieu de 28 765 théoriques)

### Metafields — Analyse approfondie (24 juin 2026)

- Vérification des filtres Magento live sur dandoy-sports.com (6 catégories crawlées)
- Mapping : 12 filtres reproduisent l'existant Magento, 5 nouveaux possibles
- `custom.technology` : 77 valeurs — affichage fiche produit uniquement (pas de filtre)
- Choix prédéfinis documentés pour 15 metafields (validation Shopify Admin)
- Page metafields scindée en 3 dans la doc MkDocs :
  - Définitions (types, sources, récapitulatif)
  - Choix prédéfinis (valeurs à copier-coller)
  - Filtrage & Affichage (comparaison Magento, config Search & Discovery)

### Documentation (17–24 juin 2026)

| Document | Contenu |
|---|---|
| `matrice_data_mapping_products.md` | Mapping complet : champs, variantes, metafields, tags, champs ignorés |
| `metafields_shopify.md` | 19 metafields : définitions, choix prédéfinis, filtrage & affichage |
| `custom_options_shopify.md` | Gluing, Lacquering, Edge tape → line item properties + code Liquid |
| `gestion_langues_shopify.md` | Stratégie FR/NL, workflow Matrixify Translations |
| `multi_sites_shopify.md` | Option A (instance unique) vs B (deux boutiques) + chiffres par domaine |
| `bundles_shopify.md` | 105 bundles : 17 promos 3=4 → remises auto, 4 divers → app Bundles |
| `regles_import_matrixify.md` | Règles CSV, commandes, variantes, images, metafields |
| `redirections_301.md` | Stratégie SEO, types de redirections, workflow |
| `GUIDE_PRESTATAIRE.md` | Guide prestataire stock sync : flux SFTP, config Stock Sync, checklist |
| `README.md` | Vue d'ensemble projet + commandes |
| Site MkDocs (05_DOCS/) | 15 pages, déployé via GitHub Pages |
| `contraintes-techniques.md` | 12 contraintes techniques (Trustpilot, Variant Image, plan Matrixify) |
| `quick-start.md` | Mode d'emploi en 8 étapes (test sample → import → purge) |
| `import/customers.md` | Migration clients : déduplication, mapping, mots de passe, post-migration |

---

## Décisions en attente

| Sujet | Options | Recommandation | Impact |
|---|---|---|---|
| **Multi-sites** | A : instance unique + Markets / B : deux boutiques | **Option A** (stock unifié, pas de survente) | Conditionne tout le reste |
| **Custom options** | Line item properties / App tierce | **Line item properties** (natif, gratuit) | Code thème à ajouter |
| **Livraison tables** (33 produits) | App tierce / Variante Shopify | **App tierce** (prix variables 41–116 €) | Coût mensuel |

---

## Reste à faire

| Sujet | Priorité | Statut |
|---|---|---|
| Plan de migration | ~~À faire~~ | **Fait** — 5 phases documentées ([Plan de migration](./import/plan-migration.md)) |
| Décision multi-sites (A ou B) | **Haute** | En attente validation client |
| Import test complet Matrixify | **Haute** | Sample testé OK, import complet à lancer (Phase 1) |
| Configuration metafields (choix prédéfinis) | Moyenne | Documenté — Phase 1 |
| Configuration Search & Discovery (filtres) | Moyenne | Documenté — Phase 1 |
| Migration clients | ~~À évaluer~~ | **Fait** — `shopify_customers.csv` prêt (41 020 clients) |
| Migration commandes | ~~À évaluer~~ | **Fait** — `shopify_orders.csv` prêt (37 430 commandes avec line items) |
| Plan Matrixify | ~~À évaluer~~ | **Enterprise ($200/mois)** — 1 mois, puis Basic |
| Stock Sync (config SFTP + mapping SKU) | **Haute** | **Documenté** — guide prestataire prêt (Phase 2) |
| Bundle products (105) | ~~Moyenne~~ | **Documenté** — remises auto Shopify (Phase 2) |
| Pages CMS Magento | Basse | Non commencé (Phase 2) |
| Thème Shopify + branding Butterfly | Hors périmètre data | Phase 2 |

---

## Historique des commits

| Date | Commit | Description |
|---|---|---|
| 25 juin | `aa38600` | Section plan Matrixify dans contraintes techniques |
| 25 juin | `d4dd849` | Page documentation migration clients |
| 25 juin | `9f41f6f` | Ajout customers dans regenerate_all.sh |
| 25 juin | `d5a91f8` | Script conversion clients (41 020 dédupliqués) |
| 25 juin | `120bd5f` | Documentation Trustpilot widget Liquid |
| 25 juin | `eeb2efc` | Retrait Variant Image (éviter doublon galerie) |
| 25 juin | `fd70d2c` | Fix sample + ajout sample dans regenerate_all.sh |
| 24 juin | `2bc9b75` | Restructuration page metafields en 3 pages MkDocs |
| 24 juin | `6ebe17d` | Ajout filtres Magento live + usage Shopify au tableau metafields |
| 24 juin | `8b96dd2` | Colonne Simple/Multiple dans récapitulatif metafields |
| 24 juin | `a9252e8` | custom.technology → affichage uniquement (pas de choix prédéfinis) |
| 24 juin | `93de0db` | Choix prédéfinis technology (77 valeurs) + gender |
| 24 juin | `2e5ec37` | Choix prédéfinis pour 14 metafields |
| 24 juin | `fed696b` | Matrice de mapping complète |
| 24 juin | `d0bc981` | Fix types metafields : promotion et shoe_type → list |
| 24 juin | `bd768ba` | Tables and Nets → Option1 = Color |
| 24 juin | `77aa9b4` | Page contraintes techniques (10 contraintes + risques) |
| 24 juin | `f14f8f7` | Fix options vides (erreur Matrixify Xushaofa Balls) |
| 23 juin | `3274cb8` | Fix incohérences doc (audit global) |
| 23 juin | `da3216c` | Quick Start (8 étapes) |
| 23 juin | `0da7df7` | Étape test sample dans Quick Start |
| 23 juin | `cea6c3d` | Fix liens doc MkDocs |
| 23 juin | `59caffd` | Site MkDocs Material + GitHub Pages |
| 22 juin | `cd476f5` | Nettoyage .gitignore (CSV générés exclus) |
| 22 juin | `97a736b` | regenerate_all.sh + fichiers PURGE |
| 22 juin | `a12d458` | Guide prestataire stock sync |
| 22 juin | `4259c2a` | Documentation stratégie bundles |
| 22 juin | `6ecc8d0` | 37 smart collections + 22 tags sous-catégories |
| 22 juin | `4b56906` | Traductions, redirections 301, documentation multi-sites/langues/Matrixify |
| 19 juin | `cf6c1d7` | Structure projet, custom options, matrice de mapping |
| 17 juin | `e3269b2` | 19 metafields + documentation metafields |
| 17 juin | `f859b1a` | Commit initial : script de conversion, screenshots, CLAUDE.md |
