# Avancement Migration Magento → Shopify — Dandoy-Sports / Butterfly TT

Dernière mise à jour : **30 juillet 2026**

> **Décision client (29 juillet 2026) : Option B retenue** — deux boutiques Shopify séparées
> (Dandoy-Sports plan complet + Butterfly TT plan Basic), et non l'instance unique (Option A)
> précédemment recommandée. Voir [Architecture multi-sites](./architecture/multi-sites.md).
> Tous les scripts de génération produisent désormais une paire de fichiers `_dandoy` /
> `_butterfly` par entité (produits, traductions, collections, redirections, clients,
> commandes).

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
│   │   ├── validate_shopify_csv.py              ← validation post-régénération (SKU, options, handles)
│   │   └── regenerate_all.sh                    ← tout régénérer (8 étapes)
│   ├── SCREENSHOTS_CATALOGUE/                   (8 captures Magento)
│   ├── THEME/                                   ← export thème Horizon (non versionné pour l'instant)
│   ├── plan-matrixify.png
│   ├── matrice_data_mapping_products.md
│   ├── metafields_shopify.md
│   ├── custom_options_shopify.md
│   ├── gestion_langues_shopify.md
│   ├── multi_sites_shopify.md
│   ├── bundles_shopify.md
│   ├── regles_import_matrixify.md
│   ├── trustpilot-widgets.md
│   ├── doublons_variantes_a_corriger.csv        ← 36 doublons résiduels à corriger dans Magento
│   └── avancement_migration.md
├── 03_SEO_AND_REDIRECTS/                        (gitignorés)
│   ├── shopify_redirects_dandoy.csv             (2 045 redirections)
│   ├── shopify_redirects_butterfly.csv          (380 redirections)
│   └── redirections_301.md
├── 04_SHOPIFY_IMPORTS/                          (CSV gitignorés sauf sample — 1 jeu par boutique)
│   ├── shopify_products_dandoy.csv              (22 223 lignes — 4 183 produits)
│   ├── shopify_products_butterfly.csv           (4 905 lignes — 849 produits)
│   ├── shopify_translations_dandoy.csv          (5 768 lignes)
│   ├── shopify_translations_butterfly.csv       (1 233 lignes)
│   ├── shopify_collections_dandoy.csv           (37 collections)
│   ├── shopify_collections_butterfly.csv        (37 collections)
│   ├── shopify_customers_dandoy.csv             (33 357 clients)
│   ├── shopify_customers_butterfly.csv          (11 404 clients)
│   ├── shopify_orders_dandoy.csv                (71 096 lignes — 23 823 commandes)
│   ├── shopify_orders_butterfly.csv             (28 725 lignes — 13 607 commandes)
│   ├── shopify_products_sample_dandoy.csv       (versionné)
│   ├── shopify_products_sample_butterfly.csv    (versionné)
│   ├── *_PURGE.csv (×6)
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

Un jeu de fichiers par boutique (Option B — voir décision ci-dessus). Les 199 produits
partagés (35 actifs) et les clients enregistrés sur les deux marques sont dupliqués dans les
deux jeux ; chaque commande n'apparaît que dans un seul jeu (boutique d'origine).

| Fichier (Dandoy / Butterfly) | Lignes | Contenu |
|---|---|---|
| `shopify_products_dandoy.csv` / `_butterfly.csv` | 22 223 / 4 905 | 4 183 / 849 produits + 20 metafields + 22 tags sous-catégories + tag `dandoy`/`butterfly` |
| `shopify_translations_dandoy.csv` / `_butterfly.csv` | 5 768 / 1 233 | Traductions FR/NL |
| `shopify_collections_dandoy.csv` / `_butterfly.csv` | 58 / 58 | 37 smart collections (16 top-level + 21 sous-catégories) |
| `shopify_redirects_dandoy.csv` / `_butterfly.csv` | 2 045 / 380 | Redirections 301 (produits actifs + catégories, scopées par boutique) |
| `shopify_customers_dandoy.csv` / `_butterfly.csv` | 33 357 / 11 404 | Clients dédupliqués + adresse par défaut + tags source |
| `shopify_orders_dandoy.csv` / `_butterfly.csv` | 71 096 / 28 725 | 23 823 / 13 607 commandes avec line items |
| `*_PURGE.csv` (×6) | — | Fichiers de suppression Matrixify pour repartir à zéro entre tests |
| `shopify_products_sample_dandoy.csv` / `_butterfly.csv` | — | Échantillon (tous types) |

### Ordre d'import recommandé (à répéter dans chaque boutique)

1. `shopify_products_sample_{dandoy|butterfly}.csv` — test, vérifier, supprimer manuellement
2. `shopify_products_{dandoy|butterfly}.csv` — produits + variantes + metafields + tags
3. `shopify_collections_{dandoy|butterfly}.csv` — collections (auto-remplies via tags/types)
4. `shopify_customers_{dandoy|butterfly}.csv` — clients + adresses
5. Activer les langues FR et NL (+ EN pour Dandoy) dans Settings → Languages
6. `shopify_translations_{dandoy|butterfly}.csv` — traductions
7. `shopify_redirects_{dandoy|butterfly}.csv` — redirections 301

### Régénération

Après mise à jour de l'export Magento :

```bash
bash 02_ANALYSIS_AND_MAPPING/SCRIPTS/regenerate_all.sh
```

Régénère les fichiers des deux boutiques en une seule commande.

### Purge (pour repartir à zéro entre tests)

Importer via Matrixify dans l'ordre inverse, dans chaque boutique :

1. `shopify_redirects_{dandoy|butterfly}_PURGE.csv`
2. `shopify_collections_{dandoy|butterfly}_PURGE.csv`
3. `shopify_products_{dandoy|butterfly}_PURGE.csv`

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

### Custom options — metafield par produit (9 juillet 2026)

- Constat : une logique thème basée uniquement sur `product.type` suraffiche les sélecteurs
  Gluing/Edge tape/Lacquering — 15,6% des Rubbers et 27,7% des Blades n'ont en réalité aucune
  de ces options (analyse produit par produit sur `export_magento_products_all.csv`)
- `magento_to_shopify.py` extrait désormais la colonne source `custom_options` vers un nouveau
  metafield `custom.available_options` (list, 20ᵉ metafield), avec union depuis les SKUs enfants
  pour les produits *grouped*
- Le thème peut ainsi n'afficher que les sélecteurs pertinents par produit au lieu d'une
  condition générique par type — voir [Custom options](./mapping/custom-options.md)
- Correction au passage : Rackets avec option Gluing = 39 produits (doc indiquait 20)

### Tests Matrixify & corrections du pipeline (9–10 juillet 2026)

- **9 juillet** : validation locale ajoutée (`validate_shopify_csv.py`) et corrections dans
  `magento_to_shopify.py` suite à un premier test Matrixify (407/1104 échecs) — Thickness/Color
  Rubbers, collisions de Handle, doublons de variantes (495 → 36 résiduels), type du metafield
  `custom.environment` aligné sur l'Admin Shopify.
- **10 juillet** : test Matrixify sur le catalogue complet (272/25 514 échecs, tous déjà
  connus), découverte de 282 Titles Butterfly en néerlandais (traduction EN manquante côté
  Magento), fix de l'import des collections (mauvais en-tête de règle Matrixify), et
  intégration + correctif du block Custom options sur le thème Horizon (champs hors formulaire).

### Migration vers deux boutiques séparées — Option B (29–30 juillet 2026)

- **29 juillet** : décision client — Option B retenue (deux boutiques Shopify séparées,
  Butterfly TT en plan Basic) au lieu de l'instance unique + Markets (Option A).
- **30 juillet** : tous les scripts adaptés pour générer une paire de fichiers `_dandoy` /
  `_butterfly` par entité :
  - `magento_to_shopify.py` : fonction `brand_scope()` (basée sur `product_websites`) route
    chaque produit vers le(s) fichier(s) approprié(s) ; les 199 produits partagés (35 actifs)
    sont dupliqués dans les deux catalogues, tagués `dandoy,butterfly` dans les deux
  - `generate_collections.py` : mêmes 37 règles de smart collections écrites dans les deux
    fichiers (évaluées localement par le catalogue de chaque boutique)
  - `generate_redirects.py` : redirections scopées par boutique (un produit/catégorie absent
    d'un catalogue ne génère pas de redirection dans ce fichier)
  - `magento_to_shopify_customers.py` : clients enregistrés sur les deux marques dupliqués
    dans les deux fichiers
  - `magento_to_shopify_orders.py` : chaque commande n'appartient qu'à une seule boutique
    (pas de duplication, contrairement aux produits/clients)
  - `regenerate_all.sh` : sample et purge générés par boutique (6 fichiers de purge)
  - `validate_shopify_csv.py` : validation indépendante par boutique
- Fichiers obsolètes de l'ancienne architecture mono-boutique supprimés
  (`shopify_products.csv`, `shopify_collections.csv`, etc.)

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

| Sujet | Options | Décision | Impact |
|---|---|---|---|
| **Multi-sites** | A : instance unique + Markets / B : deux boutiques | **Option B retenue (29 juillet 2026)** — deux boutiques, Butterfly en plan Basic | Scripts adaptés — voir ci-dessus |
| **Custom options** | Line item properties / App tierce | **Line item properties** (natif, gratuit) | Code thème à ajouter |
| **Livraison tables** (33 produits) | App tierce / Variante Shopify | **App tierce** (prix variables 41–116 €) | Coût mensuel |
| **Plan Basic Butterfly** | — | À valider | Limitations à vérifier (rapports pro, shipping tiers calculé, comptes staff) |

---

## Reste à faire

| Sujet | Priorité | Statut |
|---|---|---|
| Plan de migration | ~~À faire~~ | **Fait** — 5 phases documentées ([Plan de migration](./import/plan-migration.md)) |
| Décision multi-sites (A ou B) | ~~Haute~~ | **Fait** — Option B retenue, scripts adaptés (29-30 juillet 2026) |
| Import test complet Matrixify | ~~Haute~~ | **Fait** — 272/25 514 échecs, tous identifiés (voir ci-dessus, sur l'ancien catalogue unique — à retester par boutique) |
| 36 doublons de variantes (données Magento) | **Haute** | À corriger manuellement — [Doublons de variantes](./mapping/doublons-variantes.md) |
| 282 Titles Butterfly en néerlandais | **Haute** | Traduction EN manquante — action requise côté Butterfly avant go-live |
| Vérifier limitations plan Basic (Butterfly) | **Haute** | À faire avant validation finale de l'Option B |
| `custom.blade_layers = "4"` refusé (7 produits Tibhar) | Moyenne | Valeur à ajouter aux choix prédéfinis dans l'Admin Shopify |
| Configuration metafields (choix prédéfinis) | Moyenne | Documenté — Phase 1 |
| Configuration Search & Discovery (filtres) | Moyenne | Documenté — Phase 1 |
| Migration clients | ~~À évaluer~~ | **Fait** — `shopify_customers_{dandoy\|butterfly}.csv` prêts (33 357 / 11 404 clients) |
| Migration commandes | ~~À évaluer~~ | **Fait** — `shopify_orders_{dandoy\|butterfly}.csv` prêts (23 823 / 13 607 commandes) |
| Plan Matrixify | ~~À évaluer~~ | **Enterprise ($200/mois)** — 1 mois, puis Basic |
| Stock Sync (config SFTP + mapping SKU) | **Haute** | **Documenté** — guide prestataire prêt (Phase 2), à dupliquer sur les 2 boutiques |
| Bundle products (105) | ~~Moyenne~~ | **Documenté** — remises auto Shopify (Phase 2) |
| Pages CMS Magento | Basse | Non commencé (Phase 2) |
| Thème Shopify + branding Butterfly | Hors périmètre data | Phase 2 — 2 thèmes à prévoir (Option B) |

---

## Historique des commits

| Date | Commit | Description |
|---|---|---|
| 10 juillet | `01fd804` | Fix import collections Matrixify (en-tête et valeurs de règle) |
| 10 juillet | `8a0c348` | Fix champs Custom options hors formulaire produit (thème Horizon) |
| 10 juillet | `9145c31` | Doc intégration Custom options thème Horizon |
| 10 juillet | `2bdc8e8` | Doc 282 Titles Butterfly en néerlandais (traduction EN manquante) |
| 10 juillet | `67c162b` | Page MkDocs doublons de variantes résiduels |
| 10 juillet | `b0865de` | Rapport CSV des 36 doublons de variantes résiduels |
| 9 juillet | `19ee3a8` | Doc écart de prix TVA .com vs .eu |
| 9 juillet | `8f891ef` | Doc metafield `custom.available_options` |
| 9 juillet | `8e9b6d5` | Suivi avancement — travail `custom.available_options` |
| 9 juillet | `e5aa404` | Metafield `custom.available_options` piloté à l'import (Gluing/EdgeTape/Lacquering) |
| 9 juillet | `30ac905` | Sync doc type liste `custom.environment` |
| 9 juillet | `22be564` | Fix type metafield `custom.environment` (Admin Shopify) |
| 9 juillet | `2d4b9ad` | Ajout validation post-régénération (`validate_shopify_csv.py`) |
| 9 juillet | `5197cee` | Fix incohérences d'options de variantes (échecs import Matrixify) |
| 30 juin | `bdc11c0` | Clarification `.com` hors UE dans l'architecture Shopify Markets |
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
