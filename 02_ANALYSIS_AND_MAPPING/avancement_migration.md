# Avancement Migration Magento → Shopify — Dandoy-Sports / Butterfly TT

Dernière mise à jour : **22 juin 2026**

---

## Arborescence du projet

```
dandoy/
├── 01_DATA_RAW/
│   └── export_magento_products_all.csv          (91 Mo, gitignored)
├── 02_ANALYSIS_AND_MAPPING/
│   ├── SCRIPTS/
│   │   ├── magento_to_shopify.py                ← script principal (produits + traductions)
│   │   ├── generate_redirects.py                ← script redirections 301
│   │   └── generate_collections.py              ← script smart collections
│   ├── SCREENSHOTS_CATALOGUE/                   (8 captures Magento)
│   ├── matrice_data_mapping_products.md
│   ├── metafields_shopify.md                    (19 metafields)
│   ├── custom_options_shopify.md                (Gluing, Lacquering, livraison)
│   ├── gestion_langues_shopify.md               (FR/NL workflow)
│   ├── multi_sites_shopify.md                   (Option A vs B)
│   ├── regles_import_matrixify.md               (règles d'import)
│   └── avancement_migration.md                  (ce fichier)
├── 03_SEO_AND_REDIRECTS/
│   ├── shopify_redirects.csv                    (2 368 redirections)
│   └── redirections_301.md
└── 04_SHOPIFY_IMPORTS/
    ├── shopify_products.csv                     (25 514 lignes, gitignored)
    ├── shopify_translations.csv                 (6 723 lignes)
    ├── shopify_collections.csv                  (58 lignes, 37 collections)
    └── shopify_products_sample.csv              (10 produits)
```

---

## Fichiers d'import Shopify prêts

| Fichier | Lignes | Contenu |
|---|---|---|
| `shopify_products.csv` | 25 514 | 4 834 produits EN + 19 metafields + 22 tags sous-catégories |
| `shopify_translations.csv` | 6 723 | Traductions FR (93% couvert) + NL (71% couvert) |
| `shopify_collections.csv` | 58 | 37 smart collections (16 top-level + 21 sous-catégories) |
| `shopify_redirects.csv` | 2 368 | Redirections 301 (produits actifs + catégories) |
| `shopify_products_sample.csv` | 53 | Échantillon 10 produits (tous types) |

### Ordre d'import recommandé

1. `shopify_products.csv` — produits + variantes + metafields + tags
2. `shopify_collections.csv` — collections (se remplissent automatiquement via les tags/types)
3. `shopify_translations.csv` — traductions FR/NL (après activation des langues)
4. `shopify_redirects.csv` — redirections 301 (après vérification que les URLs cibles existent)

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
  - Balls → Quantity + Color
  - Cleaners → Quantity
  - Autres → fallback sur suffixe du nom
- 19 metafields custom (blade_category, pimples, hardness, technology, gender…)
- Export des traductions FR/NL depuis eu_fr, bt_be_fr, eu_nl

### Collections Shopify (22 juin 2026)

- 22 tags de sous-catégories ajoutés aux produits (polos, suits, tables, bags…)
- 37 smart collections générées :
  - **16 top-level** : Blades, Rubbers, Clothing, Shoes, Balls, Tables & Nets, Rackets, Robots, Accessories, Cleaners & Glue, Clubs, Luggages, Padel, Pickleball, Promo Special, Liquidations Football
  - **21 sous-catégories** : Polos, Shorts, T-Shirts, Jackets, Socks, Suits, Sweater, Bags, Bat Covers, Tables, Nets, Cleaners, Glue, Coloured Rubbers, Robots Machines, Robot Accessories, Racket Accessories, Textile Accessories, Football Jerseys/Shorts/Socks
- Règles basées sur Product Type + Product Tag (remplissage automatique)

### Redirections 301 (22 juin 2026)

- Génération des redirections produits + catégories
- Vérification HTTP sur le site Magento live : seuls les produits actifs et visibles ont une URL
- Résultat : 2 368 redirections utiles (au lieu de 28 765 théoriques)
- Enfants simples et produits désactivés exclus (déjà en 404 sur Magento)

### Documentation

| Document | Contenu |
|---|---|
| `matrice_data_mapping_products.md` | Mapping colonnes Magento → Shopify |
| `metafields_shopify.md` | 19 metafields : types, valeurs, usage filtrage/affichage |
| `custom_options_shopify.md` | Gluing, Lacquering, Edge tape → line item properties |
| `gestion_langues_shopify.md` | Stratégie FR/NL, workflow Matrixify Translations |
| `multi_sites_shopify.md` | Option A (instance unique) vs B (deux boutiques) |
| `regles_import_matrixify.md` | Règles CSV, commandes, variantes, images, metafields |
| `redirections_301.md` | Stratégie SEO, types de redirections, workflow |

---

## Décisions en attente

| Sujet | Options | Recommandation | Impact |
|---|---|---|---|
| **Multi-sites** | A : instance unique + Markets / B : deux boutiques | **Option A** (stock unifié, pas de survente) | Conditionne tout le reste |
| **Custom options** | Line item properties / App tierce | **Line item properties** (natif, gratuit) | Code thème à ajouter |
| **Livraison tables** (33 produits) | App tierce / Variante Shopify | **App tierce** (prix dynamique) | Coût mensuel |

---

## Reste à faire

| Sujet | Priorité | Statut |
|---|---|---|
| Décision multi-sites (A ou B) | **Haute** | En attente validation client |
| Bundle products (105 ignorés) | Moyenne | Non commencé — décision : scinder ou app ? |
| Stock Sync (config SFTP + mapping SKU) | **Haute** | Post-import |
| Migration clients / commandes | À évaluer | Fresh start ou historique ? |
| Pages CMS Magento | Basse | Non commencé |
| Thème Shopify + branding Butterfly | Hors périmètre data | — |

---

## Historique des commits

| Date | Commit | Description |
|---|---|---|
| 22 juin | `6ecc8d0` | 37 smart collections + 22 tags sous-catégories |
| 22 juin | `fd25dc8` | Document d'avancement migration |
| 22 juin | `4b56906` | Traductions, redirections 301, documentation multi-sites/langues/Matrixify |
| 19 juin | `cf6c1d7` | Structure projet, custom options, matrice de mapping |
| 17 juin | `e3269b2` | 19 metafields + documentation metafields |
| 17 juin | `ae22acd` | .gitkeep pour dossiers vides |
| 17 juin | `f859b1a` | Commit initial : script de conversion, screenshots, CLAUDE.md |
