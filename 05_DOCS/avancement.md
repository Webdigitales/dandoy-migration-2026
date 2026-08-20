# Avancement Migration Magento → Shopify — Dandoy-Sports / Butterfly TT

Dernière mise à jour : **20 août 2026**

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
│   ├── export_order_all_2025_2026.csv
│   ├── gift_cards_export_file.csv               (841 cartes, 281 actives)
│   ├── cart_price_rules.csv, customer_group.csv (remises club — voir club-b2b.md)
│   └── tax_rates.csv
├── 02_ANALYSIS_AND_MAPPING/
│   ├── SCRIPTS/
│   │   ├── magento_to_shopify.py                ← produits + traductions
│   │   ├── generate_collections.py              ← smart collections
│   │   ├── generate_redirects.py                ← redirections 301
│   │   ├── magento_to_shopify_customers.py      ← clients
│   │   ├── magento_to_shopify_orders.py         ← commandes 2025-2026
│   │   ├── generate_companies.py                ← B2B Companies clubs (Dandoy uniquement)
│   │   ├── build_orders_stratified_sample.py    ← échantillon de test à 950 commandes (cas limites)
│   │   ├── validate_shopify_csv.py              ← validation post-régénération (SKU, options, handles)
│   │   ├── migrate_giftcards_shopify.py         ← migration cartes cadeaux (API, hors regenerate_all.sh)
│   │   ├── get_shopify_access_token.py          ← obtention token API (OAuth, hors regenerate_all.sh)
│   │   └── regenerate_all.sh                    ← tout régénérer (9 étapes)
│   ├── SCREENSHOTS_CATALOGUE/                   (8 captures Magento)
│   ├── SCREENSHOTS_MIGRATION_TOOLING/           (app privée API)
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
│   └── club_discount_mapping.csv                ← 88 clubs → taux → catalog Shopify (gitignoré)
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
│   ├── shopify_companies_dandoy.csv             (85 companies — clubs partenaires, Dandoy uniquement)
│   ├── shopify_orders_dandoy.csv                (99 510 lignes — 24 896 commandes, avec Fulfillment Lines)
│   ├── shopify_orders_butterfly.csv             (44 159 lignes — 14 198 commandes, avec Fulfillment Lines)
│   ├── shopify_orders_stratified_{dandoy|butterfly}.csv  ← échantillon 950 commandes (cas limites, test Matrixify)
│   ├── giftcards_migration_report_{dandoy|butterfly}.csv ← rapport d'audit migration gift cards (non versionné)
│   ├── shopify_products_sample_dandoy.csv       (versionné)
│   ├── shopify_products_sample_butterfly.csv    (versionné)
│   ├── shopify_customers_sample_dandoy.csv      (versionné — 10 clients)
│   ├── shopify_customers_sample_butterfly.csv   (versionné — 10 clients)
│   ├── shopify_orders_sample_dandoy.csv         (versionné — 5 commandes)
│   ├── shopify_orders_sample_butterfly.csv      (versionné — 5 commandes)
│   ├── *_PURGE.csv (×8)
│   └── ERRORS/                                  (rapports d'import Matrixify)
├── 05_DOCS/                                     (source MkDocs — GitHub Pages)
│   ├── index.md, quick-start.md, contraintes-techniques.md
│   ├── avancement.md (état actuel), journal-migration.md (historique détaillé)
│   ├── mapping/        (matrice, metafields ×3, custom-options, bundles, club-b2b, doublons-variantes)
│   ├── architecture/   (multi-sites, langues)
│   ├── import/         (plan-migration, matrixify, redirections, customers, orders, gift-cards, api-credentials)
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
| `shopify_companies_dandoy.csv` | 2 086 (85 companies) | B2B Companies clubs partenaires (Dandoy uniquement — Butterfly bloqué, voir [Remises club & B2B](./mapping/club-b2b.md)) |
| `shopify_orders_dandoy.csv` / `_butterfly.csv` | 99 510 / 44 159 | 24 896 / 14 198 commandes avec line items + Fulfillment Lines (39 094 au total) |
| `shopify_orders_stratified_dandoy.csv` / `_butterfly.csv` | — | Échantillon de test à 950 commandes ciblant les cas limites (devise, paiement pending, expédition partielle, grosses commandes, tous stores/passerelles) |
| `*_PURGE.csv` (×8) | — | Fichiers de suppression Matrixify pour repartir à zéro entre tests (produits, collections, redirections, commandes × 2 boutiques) |
| `shopify_products_sample_dandoy.csv` / `_butterfly.csv` | — | Échantillon produits (tous types) |
| `shopify_customers_sample_dandoy.csv` / `_butterfly.csv` | — | Échantillon clients (5 avec adresse + 5 sans) |
| `shopify_orders_sample_dandoy.csv` / `_butterfly.csv` | — | Échantillon commandes (5 commandes complètes avec line items) |
| `giftcards_migration_report_dandoy.csv` / `_butterfly.csv` | — | Rapport d'audit de la migration gift cards (statut par carte, non versionné) |

### Ordre d'import recommandé (à répéter dans chaque boutique)

1. `shopify_products_sample_{dandoy|butterfly}.csv` — test, vérifier, supprimer manuellement
2. `shopify_products_{dandoy|butterfly}.csv` — produits + variantes + metafields + tags
3. `shopify_collections_{dandoy|butterfly}.csv` — collections (auto-remplies via tags/types)
4. `shopify_customers_{dandoy|butterfly}.csv` — clients + adresses
5. `shopify_companies_dandoy.csv` — Companies B2B (Dandoy uniquement — Catalogs créés manuellement au préalable, voir [Remises club & B2B](./mapping/club-b2b.md))
6. Activer les langues FR et NL (+ EN pour Dandoy) dans Settings → Languages
7. `shopify_translations_{dandoy|butterfly}.csv` — traductions
8. `shopify_redirects_{dandoy|butterfly}.csv` — redirections 301

### Régénération

Après mise à jour de l'export Magento :

```bash
bash 02_ANALYSIS_AND_MAPPING/SCRIPTS/regenerate_all.sh
```

9 étapes : produits + traductions → collections → redirections → customers → companies
(Dandoy uniquement) → commandes → sample → purge → validation, chacune générant les fichiers
des deux boutiques (sauf companies). Les scripts de migration gift cards
(`migrate_giftcards_shopify.py`) et d'obtention de token API (`get_shopify_access_token.py`)
sont **volontairement exclus** de cette régénération — effets de bord réels côté API Shopify,
pas de simple génération de fichier local.

La validation (`validate_shopify_csv.py`) rejoue en local les règles qui font échouer un
import Matrixify : SKU dupliqués entre produits, combinaisons de variantes dupliquées,
options incohérentes, plafond des 100 variantes, prix manquant/négatif, handles orphelins.
Sort en erreur (code 1) sans empêcher la génération des autres fichiers. Validée
indépendamment pour chaque boutique.

### Purge (pour repartir à zéro entre tests)

Importer via Matrixify dans l'ordre inverse, dans chaque boutique :

1. `shopify_orders_{dandoy|butterfly}_PURGE.csv` (`Command = DELETE`, une ligne par `Name`)
2. `shopify_redirects_{dandoy|butterfly}_PURGE.csv`
3. `shopify_collections_{dandoy|butterfly}_PURGE.csv`
4. `shopify_products_{dandoy|butterfly}_PURGE.csv`

Les commandes importées via l'API Shopify (comme le fait Matrixify) restent supprimables même
une fois fulfilled — contrairement à l'annulation en masse (`Cancel`), bloquée dès qu'une
commande est fulfilled.

---

## Documentation

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
| Site MkDocs (05_DOCS/) | 23 pages, déployé via GitHub Pages |
| `contraintes-techniques.md` | 14 contraintes techniques (Trustpilot, Variant Image, Companies B2B, gift cards/promo, plan Matrixify) |
| `quick-start.md` | Mode d'emploi en 9 étapes (test sample → import → Companies → purge) |
| `import/customers.md` | Migration clients : déduplication, mapping, mots de passe, post-migration |
| [Historique des commandes](./import/orders.md) | Script conversion, fiscalité, Fulfillment Line, champ Note, liaisons clients, import Matrixify |
| [Plan de migration](./import/plan-migration.md) | Plan 5 phases : foundation → theming → recette → pré-go-live → go-live |
| [Chèques cadeaux](./import/gift-cards.md) | Migration 281 cartes actives (9 247,49 €) — Option B (API), script écrit, test live confirmé |
| [Identifiants API](./import/api-credentials.md) | App privée `Migration Tooling`, workflow Authorization Code Grant (2026 Dev Dashboard), token Dandoy obtenu |
| [Remises club & B2B](./mapping/club-b2b.md) | 88 clubs, Companies B2B deux boutiques, Shopify Plus confirmé Dandoy, Butterfly bloqué par limite catalogues |
| [Doublons de variantes](./mapping/doublons-variantes.md) | 36 doublons résiduels à corriger manuellement côté Magento |
| [Journal de migration](./journal-migration.md) | Récit chronologique complet + historique des commits (déplacé hors de cette page le 20 août 2026) |

---

## Décisions en attente

| Sujet | Options | Décision | Impact |
|---|---|---|---|
| **Multi-sites** | A : instance unique + Markets / B : deux boutiques | **Option B retenue (29 juillet 2026)** — deux boutiques, Butterfly en plan Basic | Scripts adaptés — voir ci-dessus |
| **Custom options** | Line item properties / App tierce | **Line item properties** (natif, gratuit) | Code thème à ajouter |
| **Livraison tables** (33 produits) | App tierce / Variante Shopify | **App tierce** (prix variables 41–116 €) | Coût mensuel |
| **Plan Basic Butterfly** | — | À valider | Limitations à vérifier (rapports pro, shipping tiers calculé, comptes staff) |
| **Fulfillment des commandes migrées** | Fulfillment Line rows / accepter "non expédiées" | **Fulfillment Line retenu et validé en live** (4 août 2026) — 2 échecs corrigés, 3ᵉ test confirmé fonctionnel (commande WEB1-0125-17658 : "Traitée", "Livré le 15 janvier 2025") | Terminé |
| **102 commandes physiques `Invoiced`-only** | Ignorer / marquer remboursées / archiver | **Marquées `refunded`** (5 août 2026, règle client) ; **archivage manuel** décidé (pas de 2ᵉ passe d'import) | Terminé |
| **Companies B2B — boutiques concernées** | Dandoy seule / deux boutiques | **Deux boutiques** (13 août 2026) — B2B ouvert à tous les plans depuis avril 2026 | Butterfly bloqué par la limite de catalogues (voir ci-dessous) |
| **Plan Dandoy-Sports** | — | **Shopify Plus confirmé** (19 août 2026) — catalogues B2B illimités | — |
| **Catalogues B2B Butterfly (Basic, max 3)** | Fusionner 2 catalogs (perte fidélité 5 clubs) / upgrade de plan | **À valider avec le client** | Bloque la création des Catalogs Butterfly et `generate_companies.py` côté Butterfly |
| **Migration chèques cadeaux** | Matrixify/Orders (nouveaux codes) / API (codes préservés) | **Option B (API) retenue** (5 août 2026), test live confirmé (20 août 2026) | Script prêt, migration complète en attente de l'import clients |
| **Langue par défaut boutique Butterfly** | Anglais (hypothèse initiale) / Néerlandais | **Néerlandais confirmé** (20 août 2026) | Invalide l'hypothèse "282 titres anglais manquants" (non-problème) et la recommandation de priorisation traduction NL — voir [Contraintes techniques](./contraintes-techniques.md), [Gestion des langues](./architecture/langues.md) |

---

## Reste à faire

| Sujet | Priorité | Statut |
|---|---|---|
| Plan de migration | ~~À faire~~ | **Fait** — 5 phases documentées ([Plan de migration](./import/plan-migration.md)) |
| Décision multi-sites (A ou B) | ~~Haute~~ | **Fait** — Option B retenue, scripts adaptés (29-30 juillet 2026) |
| Import test complet Matrixify (produits) | ~~Haute~~ | **Fait** — 272/25 514 échecs, tous identifiés (voir ci-dessus, sur l'ancien catalogue unique — à retester par boutique) |
| Import test commandes Matrixify | ~~Haute~~ | **Fait** — sample confirmé fonctionnel après 5 corrections (colonnes, adresses, line items — voir ci-dessus) |
| 36 doublons de variantes (données Magento) | **Haute** | **Confirmés inchangés (20 août 2026)** — 32 produits distincts touchés (0,6 % du catalogue), erreur bloquante Matrixify mais localisée à la ligne (le reste du produit s'importe), non urgent pour tester le pipeline mais à corriger avant le go-live définitif — [Doublons de variantes](./mapping/doublons-variantes.md) |
| 282 Titles Butterfly en néerlandais | ~~Haute~~ | **Non-problème, résolu (20 août 2026)** — hypothèse initiale fausse (`(base)` supposée EN) ; NL confirmé langue par défaut Shopify Butterfly, aucune action requise — voir [Contraintes techniques](./contraintes-techniques.md) et [Gestion des langues](./architecture/langues.md) |
| Vérifier limitations plan Basic (Butterfly) | **Haute** | À faire avant validation finale de l'Option B |
| Ajouter `Updated At` + point relais (bpost/DPD/Sendcloud) + `mollie_transaction_id` à l'export Magento | ~~Haute~~ | **Fait** (4 août 2026) — export mis à jour, mappé dans le script (`Fulfillment: Processed At` + champ `Note`) |
| Vérifier en base (`sales_order_payment.additional_information`) si un ID de transaction existe pour PayPlug, PayPal Express et Klarna (~2 850 commandes, 7,3%) — **confirmé absent** de la liste d'attributs order Magento Admin | Moyenne | À vérifier directement en base — à défaut, `Note` restera vide pour ces commandes |
| Tester en live le mécanisme Fulfillment Line (commandes) | ~~Haute~~ | **Fait** — 2 échecs corrigés le 4 août 2026, 3ᵉ test confirmé |
| `custom.blade_layers = "4"` refusé (7 produits Tibhar) | ~~Moyenne~~ | **Fait** — valeur ajoutée aux choix prédéfinis dans l'Admin Shopify |
| Configuration metafields (choix prédéfinis) | ~~Moyenne~~ | **Fait** — metafields configurés dans l'Admin Shopify |
| Configuration Search & Discovery (filtres) | Moyenne | Documenté — Phase 1 |
| Migration clients | ~~À évaluer~~ | **Fait** — `shopify_customers_{dandoy\|butterfly}.csv` prêts (33 357 / 11 404 clients), sample testé OK ; **import complet pas encore lancé** (boutique test à 563 clients seulement) |
| Migration commandes | ~~À évaluer~~ | **Fait** — `shopify_orders_{dandoy\|butterfly}.csv` prêts (24 896 / 14 198 commandes), sample + échantillon stratifié 950 testés OK |
| Plan Matrixify | ~~À évaluer~~ | **Enterprise ($200/mois)** — 1 mois, puis Basic |
| Stock Sync (config SFTP + mapping SKU) | **Haute** | **Documenté** — guide prestataire prêt (Phase 2), à dupliquer sur les 2 boutiques |
| Bundle products (105) | ~~Moyenne~~ | **Documenté** — remises auto Shopify (Phase 2) |
| 102 commandes physiques `Invoiced`-only | ~~Haute~~ | **Fait** (5 août 2026) — marquées `refunded`, archivage manuel post-import décidé |
| URLs Butterfly FR localisées (125) + catégories traduites | Moyenne | À traiter manuellement dans Shopify Admin après import (pas de source de données pour automatiser) — [Redirections 301](./import/redirections.md) |
| Companies B2B Dandoy | ~~Haute~~ | **Fait** (19 août 2026) — `shopify_companies_dandoy.csv` prêt (85 companies), pas encore importé |
| Companies B2B Butterfly | **Haute** | **Bloqué** — 4 catalogs nécessaires, limite Basic = 3 ; décision client à prendre (fusion ou upgrade plan) |
| Génération contenu Catalogs (`Included / <Catalog>` sur sheet Products) | **Haute** | Pas encore scripté — nouveau step indépendant de `generate_companies.py`, voir [Remises club & B2B](./mapping/club-b2b.md) |
| Migration chèques cadeaux (281 cartes actives, 9 247,49 €) | **Haute** | Script prêt, test live confirmé (20 août 2026, 1 carte) ; **migration complète en attente de l'import clients** (liaison par email sinon inefficace) — [Chèques cadeaux](./import/gift-cards.md) |
| App privée `Migration Tooling` + token API — Dandoy | ~~Haute~~ | **Fait** (20 août 2026) — Authorization Code Grant fonctionnel, token permanent obtenu — [Identifiants API](./import/api-credentials.md) |
| App privée `Migration Tooling` + token API — Butterfly | **Haute** | Pas commencé |
| Codes promo / cart price rules (hors remises club) | Basse | Pas dans le périmètre analysé — à vérifier si des règles actives existent en dehors du système club |
| Pages CMS Magento | Basse | Non commencé (Phase 2) |
| Thème Shopify + branding Butterfly | Hors périmètre data | Phase 2 — 2 thèmes à prévoir (Option B) |

