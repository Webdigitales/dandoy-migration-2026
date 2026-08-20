# Avancement Migration Magento → Shopify — Dandoy-Sports / Butterfly TT

Dernière mise à jour : **20 août 2026**

> ⚠️ Ce fichier est un miroir interne de `05_DOCS/avancement.md` (source MkDocs, publiée sur
> GitHub Pages). Les deux ont divergé entre le 5 et le 20 août 2026 — celui-ci contenait déjà
> les sections remboursements/échantillon stratifié, le site public avait déjà gift
> cards/identifiants API. Resynchronisés le 20 août 2026. Préférer éditer `05_DOCS/avancement.md`
> en premier à l'avenir, puis répercuter ici.

> **Décision client (29 juillet 2026) : Option B retenue** — deux boutiques Shopify séparées
> (Dandoy-Sports plan complet + Butterfly TT plan Basic), et non l'instance unique (Option A)
> précédemment recommandée. Voir `multi_sites_shopify.md`. Tous les scripts de génération
> produisent désormais une paire de fichiers `_dandoy` / `_butterfly` par entité (produits,
> traductions, collections, redirections, clients, commandes).

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
│   │   ├── generate_companies.py                ← B2B Companies clubs (Dandoy uniquement)
│   │   ├── build_orders_stratified_sample.py    ← échantillon de test à 950 commandes
│   │   ├── validate_shopify_csv.py              ← validation post-régénération (SKU, options, handles)
│   │   ├── migrate_giftcards_shopify.py         ← migration cartes cadeaux (API, hors regenerate_all.sh)
│   │   ├── get_shopify_access_token.py          ← obtention token API (OAuth, hors regenerate_all.sh)
│   │   └── regenerate_all.sh                    ← tout régénérer (9 étapes)
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
│   └── avancement_migration.md                  (ce fichier)
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
│   ├── shopify_orders_dandoy.csv                (74 535 lignes — 24 855 commandes)
│   ├── shopify_orders_butterfly.csv             (30 027 lignes — 14 196 commandes)
│   ├── shopify_products_sample_dandoy.csv       (versionné)
│   ├── shopify_products_sample_butterfly.csv    (versionné)
│   ├── shopify_customers_sample_dandoy.csv      (versionné — 10 clients)
│   ├── shopify_customers_sample_butterfly.csv   (versionné — 10 clients)
│   ├── shopify_orders_sample_dandoy.csv         (versionné — 5 commandes)
│   ├── shopify_orders_sample_butterfly.csv      (versionné — 5 commandes)
│   ├── *_PURGE.csv (×8)
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

Un jeu de fichiers par boutique (Option B). Les 199 produits partagés (35 actifs) et les
clients enregistrés sur les deux marques sont dupliqués dans les deux jeux ; chaque commande
n'apparaît que dans un seul jeu (boutique d'origine).

| Fichier (Dandoy / Butterfly) | Lignes | Contenu |
|---|---|---|
| `shopify_products_dandoy.csv` / `_butterfly.csv` | 22 223 / 4 905 | 4 183 / 849 produits + 20 metafields + 22 tags sous-catégories + tag `dandoy`/`butterfly` |
| `shopify_translations_dandoy.csv` / `_butterfly.csv` | 5 768 / 1 233 | Traductions FR/NL |
| `shopify_collections_dandoy.csv` / `_butterfly.csv` | 58 / 58 | 37 smart collections (16 top-level + 21 sous-catégories) |
| `shopify_redirects_dandoy.csv` / `_butterfly.csv` | 2 045 / 380 | Redirections 301 (produits actifs + catégories, scopées par boutique) |
| `shopify_customers_dandoy.csv` / `_butterfly.csv` | 33 357 / 11 404 | Clients dédupliqués + adresse par défaut + tags source |
| `shopify_companies_dandoy.csv` | 2 086 (85 companies) | B2B Companies clubs partenaires (Dandoy uniquement) |
| `shopify_orders_dandoy.csv` / `_butterfly.csv` | 99 510 / 44 159 | 24 896 / 14 198 commandes avec line items + Fulfillment Lines (39 094 au total) |
| `*_PURGE.csv` (×8) | — | Fichiers de suppression Matrixify pour repartir à zéro entre tests (produits, collections, redirections, commandes × 2 boutiques) |
| `shopify_products_sample_dandoy.csv` / `_butterfly.csv` | — | Échantillon produits (tous types) |
| `shopify_customers_sample_dandoy.csv` / `_butterfly.csv` | — | Échantillon clients (5 avec adresse + 5 sans) |
| `shopify_orders_sample_dandoy.csv` / `_butterfly.csv` | — | Échantillon commandes (5 commandes complètes avec line items) |

### Ordre d'import recommandé (à répéter dans chaque boutique)

1. `shopify_products_sample_{dandoy|butterfly}.csv` — test, vérifier, supprimer manuellement
2. `shopify_products_{dandoy|butterfly}.csv` — produits + variantes + metafields + tags
3. `shopify_collections_{dandoy|butterfly}.csv` — collections (auto-remplies via tags/types)
4. `shopify_customers_{dandoy|butterfly}.csv` — clients + adresses
5. Activer les langues FR et NL (+ EN pour Dandoy) dans Settings → Languages
6. `shopify_translations_{dandoy|butterfly}.csv` — traductions
7. `shopify_redirects_{dandoy|butterfly}.csv` — redirections 301

### Régénération

Après mise à jour des exports Magento :

```bash
bash 02_ANALYSIS_AND_MAPPING/SCRIPTS/regenerate_all.sh
```

9 étapes : produits + traductions → collections → redirections → customers → companies
(Dandoy uniquement) → commandes → sample → purge → validation, chacune générant les fichiers
des deux boutiques (sauf companies). `migrate_giftcards_shopify.py` et
`get_shopify_access_token.py` sont volontairement exclus (effets de bord réels côté API).

La validation (`validate_shopify_csv.py`) rejoue en local les règles qui font échouer un import
Matrixify : SKU dupliqués entre produits, combinaisons de variantes dupliquées, options
incohérentes, plafond des 100 variantes, prix manquant/négatif, handles orphelins. Sort en
erreur (code 1) sans empêcher la génération des autres fichiers. Validée indépendamment pour
chaque boutique.

### Purge (pour repartir à zéro entre tests)

Importer via Matrixify dans l'ordre inverse, dans chaque boutique :

1. `shopify_orders_{dandoy|butterfly}_PURGE.csv` (`Command = DELETE`, une ligne par `Name`)
2. `shopify_redirects_{dandoy|butterfly}_PURGE.csv`
3. `shopify_collections_{dandoy|butterfly}_PURGE.csv`
4. `shopify_products_{dandoy|butterfly}_PURGE.csv`

Les commandes importées via l'API Shopify (comme le fait Matrixify) restent supprimables même
une fois fulfilled — contrairement à l'annulation en masse (`Cancel`), bloquée par Matrixify dès
qu'une commande est fulfilled. Seules les commandes où Shopify a lui-même traité un paiement
réel ("Shopify-brokered transactions") ne peuvent pas être supprimées ; ne concerne pas nos
imports de test.

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
  condition générique par type — voir `05_DOCS/mapping/custom-options.md`
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
  - `generate_redirects.py` : redirections scopées par boutique
  - `magento_to_shopify_customers.py` : clients enregistrés sur les deux marques dupliqués
    dans les deux fichiers
  - `magento_to_shopify_orders.py` : chaque commande n'appartient qu'à une seule boutique
  - `regenerate_all.sh` : sample et purge générés par boutique (6 fichiers de purge)
  - `validate_shopify_csv.py` : validation indépendante par boutique
- Fichiers obsolètes de l'ancienne architecture mono-boutique supprimés

### Repasse documentaire complète + samples clients/commandes (30 juillet 2026)

- Revue systématique des 18 pages MkDocs + leurs mirrors `02_ANALYSIS_AND_MAPPING/` pour
  éliminer toute référence résiduelle à l'Option A ou aux anciens noms de fichiers mono-boutique
- Corrections indépendantes trouvées au passage : lien cassé `quick-start.md` →
  `mapping/metafields.md`, typo d'en-tête dans `contraintes-techniques.md`, comptage obsolète
  19→20 metafields, `custom_options_shopify.md` très en retard sur sa version 05_DOCS
- `regenerate_all.sh` génère désormais aussi des échantillons clients (10/boutique) et
  commandes (5 commandes complètes/boutique) — versionnés comme le sample produits

### Debug Matrixify commandes — 5 itérations de test réel (30 juillet 2026)

Le premier test Matrixify sur le sample commandes échouait à 100% (adresse manquante dans
l'export Magento). Après ajout des colonnes d'adresse côté Magento, 5 allers-retours de test réel
ont été nécessaires pour obtenir un import propre :

1. **Adresses manquantes** → 14 colonnes ajoutées côté export Magento (`BillingAddress.Street/
   City/Region/Postcode/Country Id/Telephone/Company` + équivalent `ShippingAddress.*`) ; mapping
   ajouté dans `magento_to_shopify_orders.py`, avec nettoyage du champ `Street` (tabulations +
   duplication de la ville) — ~39% des commandes ont une rue multi-lignes, 64% de celles-ci
   dupliquaient la ville
2. **Colonne `Country Code` non reconnue** par le template Orders (contrairement à Customers) →
   code ISO déplacé vers la colonne `Country` d'origine
3. **18 colonnes en échec silencieux** (`Financial Status`, `Subtotal`, `Lineitem *`, `Billing/
   Shipping Address1/2`, `Payment Method`…) → renommées vers la convention Matrixify actuelle
   `Section: Champ` (`Payment: Status`, `Line: Name`, `Billing: Address 1`, `Transaction: Payment
   Method`…), confirmée via la doc officielle Matrixify
4. **"must have at least one line item"** malgré SKU/prix/quantité présents → `Line: Type` =
   `"Line Item"` et `Line: ID` (compteur unique global) sont obligatoires, ajoutés
5. **`Line: Fulfillment Status` puis `Fulfillment Status`** → tous deux export-only (calculés
   depuis de vrais enregistrements de fulfillment Shopify, pas settable à l'import), retirés

**Import du sample confirmé fonctionnel** à l'issue de ces 5 corrections. Limitation connue : sans
un mécanisme `Fulfillment Line` (chantier séparé, plus conséquent), les commandes importées
apparaîtront comme non expédiées dans Shopify quel que soit leur statut historique réel — décision
à prendre plus tard sur l'opportunité de l'implémenter.

Au passage, découverte que l'export Magento des commandes avait une période tronquée
(30 mai 2025 → 30 juillet 2026 au lieu de janvier 2025 → aujourd'hui, -7 741 commandes) lors du
premier ajout des colonnes d'adresse — corrigé côté Magento, période complète restaurée
(39 051 commandes au total désormais, contre 37 430 avant).

### Fix taxes/remise/devise + mécanisme Fulfillment Line (4 août 2026)

- **Bug fiscal découvert en test live** (commande WEB1-0125-17658) : `Tax: Total` seul
  n'affiche pas la taxe si les line items sont eux-mêmes taxables — Matrixify l'ignore pour
  éviter une double taxation (doc officielle). Corrigé via `Line: Tax 1 Title/Rate/Price` par
  item. La remise Magento (`Discount Amount`) est TTC alors que `Line: Price` est HT — la
  soustraire brute faisait dévier le Total Shopify de 2-3 % ; conversion en HT avant
  soustraction ajoutée (`Price: Total Discount`).
- **Bug devise découvert par relecture** : 997 commandes (2,5 %, boutique WW hors UE)
  exportent un `Grand Total` en devise locale à côté d'un `Base Grand_total` en EUR, sans
  code devise explicite — envoyées à Shopify comme si le montant local était de l'EUR. Un
  taux de change dérivé par commande (`fx_rate()`) corrige tous les montants concernés
  (Subtotal, Price, Tax, Discount).
- **Mécanisme Fulfillment Line implémenté** (déblocage de la décision en attente, voir
  ci-dessous) : recherche de la doc officielle Matrixify (contredit partiellement une
  suggestion externe — Gemini proposait des colonnes `Fulfillment: Status/Date/Send Receipt`
  directement sur les lignes `Line Item`, alors que Matrixify exige une ligne séparée
  `Line: Type = 'Fulfillment Line'`, confirmé par leur documentation officielle). 99,2 % des
  commandes (38 722/39 051) ont tous leurs items à `Status = Shipped` → une ligne
  Fulfillment par commande (`Fulfillment: Status = success`, `Fulfillment: Send Receipt =
  FALSE` pour ne pas ré-notifier les clients) ; les 0,8 % restants (statuts Invoiced/Mixed)
  restent non expédiés plutôt que de deviner un état. **Non testé en live** (contrairement au
  reste du fichier) — à valider au prochain test Matrixify.
- **Date d'expédition (`Fulfillment: Processed At`) laissée vide** : aucune date fiable
  disponible côté export Magento actuel. Écarté `Bpost Drop/Delivery Date` (ne couvre que
  18 % des commandes — bpost est loin d'être le seul transporteur) et `Created At` (date de
  commande, pas d'expédition). Décidé de demander l'ajout de `Updated At` à l'export Magento
  (couvre 100 % des commandes, approximatif mais mieux que rien) — voir Reste à faire.
- **Champ `Note` identifié comme utile** : pourrait porter le point relais (bpost/DPD/
  Sendcloud) et l'ID de transaction Mollie — colonnes disponibles côté attributs Magento
  (`mollie_transaction_id`, `bpost_point_*`, `dpd_parcelshop_*`, `sendcloud_service_point_*`)
  mais absentes de l'export actuel — à demander en même temps que `Updated At`.
- **PayPlug/PayPal Express/Klarna** : aucun ID de transaction dans la liste d'attributs order
  Magento Admin (confirmé — l'utilisateur est lui-même le prestataire/dev Magento du projet,
  a vérifié directement). Probablement stocké hors des attributs order plats
  (`sales_order_payment.additional_information`) — à vérifier en base si besoin.

### Export Magento mis à jour : Fulfillment + Note débloqués (4 août 2026)

`Updated At`, les colonnes point relais (bpost/DPD/Sendcloud) et `Mollie Transaction Id`
ajoutés à `export_order_all_2025_2026.csv` (39 094 commandes, +43 vs la veille — période
glissante). Vérification et câblage dans `magento_to_shopify_orders.py` :

- **`Updated At`** : 100 % rempli, mais format différent de `Created At` (`2025-01-02
  11:11:43` vs `Jan 1, 2025 02:12:20 AM`) — `parse_date()` étendu pour reconnaître les deux
  formats. `Fulfillment: Processed At` n'est donc plus vide.
- **Point relais** : seul **Sendcloud** est réellement utilisé (23,8 % des commandes) — les
  colonnes `Bpost Point *` et `Dpd Parcelshop *` sont vides à 100 % dans ce jeu de données
  (conservées en fallback dans le code au cas où, sans coût). Correspond aux libellés "Point
  Relais - UPS/DPD/Mondial Relay" observés dans `Shipping Description` : Sendcloud est
  l'intégration meta-transporteur derrière ces méthodes.
- **`Mollie Transaction Id`** : 89,7 % rempli (cohérent avec la part Mollie des paiements).
- **`Note`** générée, ex. : `Point relais: LOPES WELKENRAEDT RUE DE L EGLISE 24, 4840
  WELKENRAEDT | Mollie: tr_cAMbSG6aTS` — 23 836/24 896 commandes Dandoy renseignées.
- Repéré au passage : le header de l'export contient désormais des colonnes `item 57`…
  `item 67` (au-delà du `MAX_ITEMS = 56` du script) — vérifié qu'aucune commande n'en utilise
  plus de 56 dans les faits, donc pas de correctif nécessaire pour l'instant ; à surveiller si
  ça change dans un futur export.

### Test live Fulfillment Line : échec 5/5 et correction (4 août 2026)

Premier test réel du mécanisme Fulfillment Line sur le sample commandes (`Import_Result_
2026-08-04_105413`) : **échec des 5 commandes**, toutes avec la même erreur — `Error saving
Fulfillment: Cannot find Line Item [N] to fulfill`, où `N` est l'ID que le script avait
attribué à la ligne `Fulfillment Line` elle-même (8, 10, 18, 23, 28).

Cause : donner un `Line: ID` neuf à la ligne `Fulfillment Line` fait que Matrixify la traite
comme un fulfillment **partiel** référençant ce `Line Item` précis — qui n'existe pas
puisque les vrais items de la commande ont des ID différents (1 à 7 par ex.). Il fallait
laisser `Line: ID` **vide** sur ces lignes pour déclencher un fulfillment complet de la
commande. Corrigé dans `magento_to_shopify_orders.py`.

**2ᵉ test** (`Import_Result_2026-08-04_110302`, après le fix ci-dessus) : erreur `Cannot find
Line Item` disparue, mais nouvelle erreur sur les 5 commandes — `You have set the
"Fulfillment: Processed At" date - therefore you also need to set the "Fulfillment: Shipment
Status" of: "delivered" or "failure".` Ajouté `Fulfillment: Shipment Status = 'delivered'`
(commandes historiques déjà expédiées).

**3ᵉ test confirmé fonctionnel** (`shopify-cmd-exemple.png`, commande WEB1-0125-17658) : statut
"Traitée" + "Livré le mercredi 15 janvier 2025" (correspond à `Fulfillment: Processed At =
2025-01-15 09:55:04`), `Note` affichée correctement (`Mollie: tr_z3dhtPdFyW`), taxe et remise
conformes (VAT 21% = 18,82€, réduction -9,96€). Écart d'1 centime observé sur le Total affiché
(108,46€ vs 108,45€ attendu/Magento) — probablement un arrondi d'affichage Shopify recalculant
à partir des composants plutôt que d'utiliser `Price: Total` tel quel ; non bloquant, à
surveiller si ça se reproduit à plus grande échelle.

### Échantillon stratifié à 950 commandes + fix adresse + finding UPDATE/CREATE (4-5 août 2026)

- **`build_orders_stratified_sample.py` ajouté** : contrairement à l'échantillon de 5 commandes
  (qui ne couvre que ce que ces 5 commandes contiennent par hasard), tire ~40-100 commandes par
  cas limite (conversion devise, paiement `pending`, expédition partielle `Invoiced`/`Mixed`,
  grosses commandes ≥10 articles, point relais Sendcloud) + couverture systématique des 7
  stores et de toutes les passerelles de paiement, plafonné à 950 commandes. Réutilise
  `build_rows()`/`SHOPIFY_COLS` du script principal (même logique de transformation).
- **1er test live** (950 commandes, dont 2 701 lignes côté Dandoy) : 2 678/2 701 lignes OK dès
  le premier essai. **23 échecs** (8 commandes), tous `"Billing and Shipping Address is not
  valid"` — adresse `Address 1` vide.
  - **Cause** : bug dans `clean_street()` — le filtre censé retirer les lignes qui dupliquent
    la ville (cas multi-lignes : `"3 Rue Pierre Corneille" / "Eaubonne"`) supprimait aussi les
    adresses **mono-ligne** où la ville est juste accolée en fin de ligne
    (`"Terwenstraat 5, Gouda"`, sans tabulation) — toute la ligne était jetée, adresse comprise.
  - **Fix** : chaque ligne est maintenant traitée indépendamment — une ligne strictement égale
    à la ville est retirée (vrai doublon), une ligne qui se termine juste par la ville ne perd
    que ce suffixe. Un balayage complet des 39 094 commandes après coup a trouvé 45 cas
    supplémentaires du même bug (58 au total) ; les ~14-15 restants sont **réellement vides
    côté Magento** (le client a tapé le nom de la ville dans le champ rue, ex. `"ajman"` / ville
    `"ajman"`) — rien à récupérer, resteront en échec à l'import quoi qu'il arrive.
- **2ᵉ test live** (même échantillon régénéré, seed identique) : les 23 erreurs d'adresse ont
  disparu, mais **30 nouveaux échecs** (4 commandes) — `"Shipping Address: Country/region not
  supported"` sur des pays valides (RO, AR) déjà acceptés ailleurs dans le même import (8
  autres commandes RO et 20 autres AR sont passées).
  - **Cause identifiée** : `SEED` fixe dans `build_orders_stratified_sample.py` → chaque
    régénération tire **exactement le même lot de 950 commandes**. Le 2ᵉ test réimportait donc
    un échantillon déjà présent dans Shopify depuis le 1er test — confirmé : 1078/1091 lignes
    avec `Command` rempli sont revenues `"UPDATE: Found by Name"` (mise à jour d'une commande
    existante), pas une création. Les 4 échecs de pays sont vraisemblablement un artefact du
    chemin **UPDATE** de Matrixify (plus strict sur le changement de pays d'une adresse
    existante que sur une création) — non représentatif d'un import réel, qui ne fera jamais
    d'UPDATE sur une commande déjà migrée. **Pas d'action prise** — à retester en création
    propre (purge préalable ou nouvelle graine) si besoin de confirmer.
- **Statut "non traité" pour les commandes `Invoiced` — investigué** (commande
  WEB1-0126-28708 signalée par le client comme "non traité" dans Shopify) : sur les 329
  commandes non totalement `Shipped`, 318 (96,7%) ont un statut item purement `Invoiced`.
  Répartition trouvée en creusant : **216/318 (68%) sont des chèques cadeau** — cohérent,
  pas d'envoi physique donc jamais de statut `Shipped` en toute logique. Les **102 restantes
  (32%) sont de vrais produits physiques** (chaussures, sacs, revêtements, vêtements),
  réparties sur les deux marques et les 7 stores, sur une période large (2 septembre 2025 →
  2 avril 2026 — certaines vieilles de 11 mois), sans pattern store/date identifiable.
  **Décision du client : garder le comportement actuel** (pas de `Fulfillment Line`, "non
  traité" dans Shopify) pour ces 102 commandes également, plutôt que de deviner. À noter pour
  référence future si le sujet revient : liste des 102 commandes non extraite, disponible sur
  demande via le même filtre (items tous `Invoiced`, aucun SKU dans `GIFT_CARD_SKUS`).
  - **Suite (5 août 2026)** : demande du client de marquer les cartes cadeau comme traitées.
    Confirmé côté catalogue (`product_type = mageworx_giftcards`, 4 SKUs : `giftcard-25/50/
    75/100`) — correspond exactement aux 216 commandes. Trouvé au passage **5 commandes
    supplémentaires** mixant un item physique déjà `Shipped` et une ligne carte cadeau
    `Invoiced` (ex. `WEB1-0525-21006`), elles aussi bloquées "non traité" à cause de la seule
    ligne carte cadeau. `magento_to_shopify_orders.py` modifié : un item est maintenant
    considéré fulfilli si `Shipped` **ou** SKU dans `GIFT_CARD_SKUS` — 221 `Fulfillment Line`
    supplémentaires générées (216 + 5). Les 102 commandes physiques non expliquées restent
    inchangées (décision précédente toujours valable, sans rapport avec les cartes cadeau).
  - **Explication du client sur les 102 commandes physiques** : il s'agit de commandes
    **remboursées car annulées par le client final**. Pas une donnée stockée côté Magento
    (le prestataire n'a pas ce champ) — c'est une **règle métier** que le client applique
    lui-même à l'œil : *"commande facturée (Invoiced) mais sans numéro d'envoi (jamais
    Shipped) = remboursée"*. Cette règle correspond exactement au signal déjà utilisé pour
    exclure ces commandes du `Fulfillment Line` — rien à demander côté export, la donnée
    n'existe pas ailleurs. **Règle validée par le client (5 août 2026) et implémentée** :
    `is_unshipped_refund()` dans `magento_to_shopify_orders.py` marque
    `Payment: Status = refunded` (au lieu de `paid`) pour toute commande dont tous les items
    sont `Invoiced` et non `Shipped`, hors cartes cadeau (`GIFT_CARD_SKUS`, gérées à part —
    elles n'atteignent jamais `Shipped` par nature et ne sont pas des remboursements). 102
    commandes concernées (39 Dandoy + 63 Butterfly). **Testé en live** via l'échantillon
    stratifié (33/102 couvertes : 8 Dandoy confirmées par le client, 25 Butterfly incluses
    mais non explicitement confirmées) — `Payment: Status = refunded` s'affiche correctement
    dans Shopify. Les 69 commandes restantes n'ont pas été testées individuellement (champ
    déjà validé depuis le 30 juillet, même code path, risque jugé faible par le client) —
    aucune action supplémentaire prévue avant l'import complet.
  - **Question soulevée : ces 102 commandes restent visibles et non archivées** dans Shopify
    (`Non traité` + `Remboursée`, mais dans la liste active). Recherché côté doc Matrixify :
    `Cancelled At`/`Cancel: Reason` (annulation) et `Closed At` (archivage) sont **tous deux
    settable uniquement en mise à jour d'une commande déjà existante** — impossible de
    créer-et-archiver/annuler en un seul import, il faudrait une 2ᵉ passe après la création.
    Autre limite : la date réelle d'annulation/archivage n'est jamais conservée, Shopify
    prend systématiquement la date de l'import. **Décision du client : archivage manuel**
    dans Shopify Admin après l'import (102 commandes, volume gérable à la main) — pas de 2ᵉ
    passe d'import à développer.

### Redirections — fix colonnes Matrixify + audit URLs localisées (6–10 août 2026)

- **6 août** : Matrixify rejetait le CSV de redirections (`"Cannot understand the uploaded
  file"`) — en-têtes `Redirect From`/`Redirect To` non reconnus, corrigés vers le vrai template
  (`ID`, `Path`, `Command`, `Target`).
- **10 août** : audit des URLs produits localisées (FR/NL) vs l'`url_key` de base — **125 URLs
  Butterfly FR** non couvertes par le script actuel, NL quasi pas concerné. Redirections de
  catégories toujours en anglais uniquement (pas de colonne `categories` renseignée sur les vues
  FR/NL dans l'export Magento). Décision : traitement manuel post-import pour les deux, pas
  d'extension de script.

### Remises club & B2B — Companies (13–19 août 2026)

- **13 août** : analyse de 93 groupes clients Magento (84 utilisés) + 88 Cart Price Rules de
  remise club permanente, sans coupon — remises segmentées par famille de produits, pas un taux
  plat. Décision : **Companies B2B sur les deux boutiques** (Shopify a ouvert le B2B à tous les
  plans depuis avril 2026).
- **19 août** : **Shopify Plus confirmé pour Dandoy-Sports** (catalogues illimités) ; Butterfly
  reste Basic (max 3 catalogues actifs). **Correction importante** : les 3 règles Butterfly
  Premium portent sur des familles de produits différentes (pas un taux combiné) → Butterfly a
  besoin de **4 catalogs**, pas 3 — dépasse la limite Basic, décision client à prendre (fusion ou
  upgrade). Confirmé que Matrixify ne peut pas créer de Catalog (manuel obligatoire côté Admin) ;
  contenu par catégorie à fournir comme liste explicite de SKU (chantier séparé, pas encore
  scripté). Les 2 Catalogs Dandoy créés. `generate_companies.py` ajouté et câblé dans
  `regenerate_all.sh` (étape 5/9, Dandoy uniquement) : `shopify_companies_dandoy.csv` généré
  (85 companies, 2 086 lignes). Détail complet : `05_DOCS/mapping/club-b2b.md`.

### Migration des chèques cadeaux — Option B, API, test live confirmé (5–20 août 2026)

- **5 août** : export `gift_cards_export_file.csv` analysé — 841 cartes, **281 actives**
  (9 247,49 €). **Option B (API `giftCardCreate`, codes préservés) retenue** plutôt que
  Matrixify/Orders (qui génère de nouveaux codes, obligerait à recontacter les 281 titulaires).
- App API `Migration Tooling — Magento2Shopify` créée et installée sur Dandoy-Sports (Dev
  Dashboard, org Partner Quai31). **Plusieurs impasses avant la bonne méthode de token** : le
  Client Credentials Grant échoue systématiquement (`shop_not_permitted`) sur boutique payante —
  restriction Shopify volontaire, réservée aux boutiques de dev. Bascule vers l'**Authorization
  Code Grant** ; `get_shopify_access_token.py` écrit (serveur de callback local temporaire, token
  jamais affiché en clair, écrit directement dans un fichier d'env non versionné) — token
  permanent obtenu le 20 août.
- **Test réel confirmé le 20 août** : 1 carte cadeau créée avec succès (code préservé, solde
  correct) — invisible au premier coup d'œil dans l'Admin (code masqué par défaut), confirmé
  exister via requête API directe.
- Liaison automatique au compte client ajoutée (recherche par email, attache `customerId`) —
  nécessite l'import complet des clients au préalable (boutique de test à 563 clients seulement
  pour l'instant, sur 33 357 attendus). Détail complet : `05_DOCS/import/gift-cards.md`,
  `05_DOCS/import/api-credentials.md`.

### Audit documentaire approfondi (20 août 2026)

Relecture complète du site MkDocs (22 pages) suite à deux semaines de travail non tracées :

- Vérification systématique des liens internes (aucun cassé) et recalcul de tous les
  chiffres depuis les CSV actuels — corrections trouvées : compteur commandes obsolète dans
  `contraintes-techniques.md` (23 823/13 607 → 24 896/14 198), étape Companies B2B absente
  de `quick-start.md` (ajoutée), nombre de pages MkDocs (15→22).
- Ajout de deux contraintes techniques jamais documentées : limite de catalogues B2B
  Butterfly (confirmée bloquante), absence de chemin CSV Matrixify pour gift cards/codes
  promo (API obligatoire).
- **Vérification des 3 points "à faire" les plus anciens** :
  - **36 doublons de variantes** : confirmés inchangés — 32 produits distincts touchés
    (0,6 % du catalogue), erreur bloquante mais localisée à la ligne.
  - **282 Titles Butterfly en néerlandais** : **retiré, fausse alerte.** Hypothèse d'origine
    fausse (`(base)` = anglais partout) — le NL est confirmé langue par défaut de la
    boutique Shopify Butterfly, et 100 % des SKU Butterfly (pas seulement les 282) ont déjà
    leur Title de base en néerlandais. Invalide aussi la recommandation "prioriser la
    traduction NL post-migration" (couverture réelle quasi complète, pas 2 %).
  - **88 clubs vs 85 companies générées** : expliqué, pas un bug — `generate_companies.py`
    filtre sur `brand == 'Dandoy'`, 3 des 88 clubs n'ont une remise que côté Butterfly.

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
| `quick-start.md` | Mode d'emploi en 9 étapes (test sample → import → Companies → purge) |
| `import/customers.md` | Migration clients : déduplication, mapping, mots de passe, post-migration |
| `import/orders.md` | Historique commandes : script conversion, liaisons clients, import Matrixify |
| `import/plan-migration.md` | Plan 5 phases : foundation → theming → recette → pré-go-live → go-live |
| `import/gift-cards.md` | Migration 281 cartes actives (9 247,49 €) — Option B (API), test live confirmé |
| `import/api-credentials.md` | App privée `Migration Tooling`, workflow Authorization Code Grant, token Dandoy obtenu |
| `mapping/club-b2b.md` | 88 clubs, Companies B2B deux boutiques, Shopify Plus confirmé Dandoy, Butterfly bloqué |
| `mapping/doublons-variantes.md` | 36 doublons résiduels à corriger manuellement côté Magento |

---

## Décisions en attente

| Sujet | Options | Décision | Impact |
|---|---|---|---|
| **Multi-sites** | A : instance unique + Markets / B : deux boutiques | **Option B retenue (29 juillet 2026)** — deux boutiques, Butterfly en plan Basic | Scripts adaptés — voir ci-dessus |
| **Custom options** | Line item properties / App tierce | **Line item properties** (natif, gratuit) | Code thème à ajouter |
| **Livraison tables** (33 produits) | App tierce / Variante Shopify | **App tierce** (prix variables 41–116 €) | Coût mensuel |
| **Plan Basic Butterfly** | — | À valider | Limitations à vérifier (rapports pro, shipping tiers calculé, comptes staff) |
| **Fulfillment des commandes migrées** | Fulfillment Line rows / accepter "non expédiées" | **Fulfillment Line retenu et validé en live** (4 août 2026) — 2 échecs corrigés, 3e test confirmé fonctionnel (commande WEB1-0125-17658 : "Traitée", "Livré le 15 janvier 2025") | Terminé |
| **102 commandes physiques `Invoiced`-only** | Ignorer / marquer remboursées / archiver | **Marquées `refunded`** (5 août 2026) ; archivage manuel décidé | Terminé |
| **Companies B2B — boutiques concernées** | Dandoy seule / deux boutiques | **Deux boutiques** (13 août 2026) | Butterfly bloqué par la limite de catalogues |
| **Plan Dandoy-Sports** | — | **Shopify Plus confirmé** (19 août 2026) | Catalogues B2B illimités |
| **Catalogues B2B Butterfly (Basic, max 3)** | Fusionner 2 catalogs / upgrade de plan | **À valider avec le client** | Bloque Companies Butterfly |
| **Migration chèques cadeaux** | Matrixify/Orders / API | **Option B (API) retenue** (5 août 2026), test live confirmé (20 août 2026) | Migration complète en attente import clients |
| **Langue par défaut boutique Butterfly** | Anglais (hypothèse initiale) / Néerlandais | **Néerlandais confirmé** (20 août 2026) | Invalide l'hypothèse "282 titres anglais manquants" et la priorisation traduction NL |

---

## Reste à faire

| Sujet | Priorité | Statut |
|---|---|---|
| Plan de migration | ~~À faire~~ | **Fait** — 5 phases documentées (`import/plan-migration.md`) |
| Décision multi-sites (A ou B) | ~~Haute~~ | **Fait** — Option B retenue, scripts adaptés (29-30 juillet 2026) |
| Import test complet Matrixify (produits) | ~~Haute~~ | **Fait** — 272/25 514 échecs, tous identifiés (voir ci-dessous, sur l'ancien catalogue unique — à retester par boutique) |
| Import test commandes Matrixify | ~~Haute~~ | **Fait** — sample confirmé fonctionnel après 5 corrections (colonnes, adresses, line items — voir ci-dessus) |
| 36 doublons de variantes (données Magento) | **Haute** | **Confirmés inchangés (20 août 2026)** — 32 produits distincts touchés (0,6 % du catalogue), erreur bloquante Matrixify mais localisée à la ligne, non urgent pour tester mais à corriger avant le go-live — `doublons_variantes_a_corriger.csv` |
| 282 Titles Butterfly en néerlandais | ~~Haute~~ | **Non-problème, résolu (20 août 2026)** — hypothèse initiale fausse (`(base)` supposée EN) ; NL confirmé langue par défaut Shopify Butterfly, aucune action requise |
| Vérifier limitations plan Basic (Butterfly) | **Haute** | À faire avant validation finale de l'Option B |
| Ajouter `Updated At` + point relais (bpost/DPD/Sendcloud) + `mollie_transaction_id` à l'export Magento | ~~Haute~~ | **Fait** (4 août 2026) — export mis à jour, mappé dans le script (`Fulfillment: Processed At` + champ `Note`) |
| Vérifier en base (table `sales_order_payment.additional_information`, pas exposée comme attribut order) si un ID de transaction existe pour PayPlug, PayPal Express et Klarna (~2 850 commandes, 7,3%) — **confirmé absent** de la liste d'attributs order Magento Admin (vérifié 4 août 2026, seul `mollie_transaction_id` y figure) | Moyenne | À vérifier directement en base — à défaut, `Note` restera vide pour ces commandes |
| Marquer les 102 commandes physiques `Invoiced`-only comme remboursées | ~~Moyenne~~ | **Fait** (5 août 2026) — règle métier du client implémentée (`is_unshipped_refund()`), pas de donnée d'export manquante finalement |
| Tester en live le mécanisme Fulfillment Line (commandes) | ~~Haute~~ | **Fait** — 2 échecs corrigés le 4 août 2026, 3e test confirmé (`shopify-cmd-exemple.png`) |
| `custom.blade_layers = "4"` refusé (7 produits Tibhar) | ~~Moyenne~~ | **Fait** — valeur ajoutée aux choix prédéfinis dans l'Admin Shopify |
| Configuration metafields (choix prédéfinis) | ~~Moyenne~~ | **Fait** — metafields configurés dans l'Admin Shopify |
| Configuration Search & Discovery (filtres) | Moyenne | Documenté — Phase 1 |
| Migration clients | ~~À évaluer~~ | **Fait** — `shopify_customers_{dandoy\|butterfly}.csv` prêts (33 357 / 11 404 clients) ; **import complet pas encore lancé** (boutique test à 563 clients) |
| Migration commandes | ~~À décider~~ | **Fait** — `shopify_orders_{dandoy\|butterfly}.csv` prêts (24 896 / 14 198 commandes), sample + échantillon stratifié 950 testés OK |
| Plan Matrixify | ~~À évaluer~~ | **Enterprise ($200/mois)** — 1 mois, puis Basic |
| Stock Sync (config SFTP + mapping SKU) | **Haute** | **Documenté** — guide prestataire prêt (Phase 2), à dupliquer sur les 2 boutiques |
| Bundle products (105) | ~~Moyenne~~ | **Documenté** — remises auto Shopify (Phase 2) |
| URLs Butterfly FR localisées (125) + catégories traduites | Moyenne | Traitement manuel dans Shopify Admin après import — `05_DOCS/import/redirections.md` |
| Companies B2B Dandoy | ~~Haute~~ | **Fait** (19 août 2026) — `shopify_companies_dandoy.csv` prêt (85 companies), pas encore importé |
| Companies B2B Butterfly | **Haute** | **Bloqué** — 4 catalogs nécessaires, limite Basic = 3, décision client à prendre |
| Génération contenu Catalogs (`Included / <Catalog>`) | **Haute** | Pas encore scripté — chantier indépendant de `generate_companies.py` |
| Migration chèques cadeaux (281 cartes actives, 9 247,49 €) | **Haute** | Script prêt, test live confirmé (20 août 2026) ; migration complète en attente de l'import clients |
| App privée `Migration Tooling` + token API — Dandoy | ~~Haute~~ | **Fait** (20 août 2026) — Authorization Code Grant fonctionnel |
| App privée `Migration Tooling` + token API — Butterfly | **Haute** | Pas commencé |
| Codes promo / cart price rules (hors remises club) | Basse | À vérifier si des règles actives existent hors du système club |
| Pages CMS Magento | Basse | Non commencé (Phase 2) |
| Thème Shopify + branding Butterfly | Hors périmètre data | Phase 2 — 2 thèmes à prévoir (Option B) |

---

## Historique des commits

| Date | Commit | Description |
|---|---|---|
| 20 août | `e2015c6` | Explication écart 88 clubs vs 85 companies générées (filtre brand Dandoy) |
| 20 août | `c9e9a0d` | Rétractation du constat "282 titres Butterfly" (NL confirmé langue par défaut) |
| 20 août | `8a28579` | Fix chiffres commandes obsolètes + étape Companies manquante dans quick-start |
| 20 août | `091e9d8` | Audit documentaire approfondi, resync des deux docs d'avancement |
| 20 août | `12901d1` | Script migration gift cards (Option B, API) + workflow identifiants API |
| 19 août | `8e9ca1f` | Ajout `generate_companies.py`, câblage dans `regenerate_all.sh` (Dandoy uniquement) |
| 19 août | `b539a82` | Résolution blocages Companies Dandoy : catalogs, adresses, rôles |
| 19 août | `6831b72` | Correction club-b2b.md : Butterfly a besoin de 4 catalogs, pas 3 |
| 19 août | `b34b477` | Correction cumul remises club + tous les rule_id Cart Price Rule documentés |
| 19 août | `5388420` | Doc stratégie Companies B2B deux boutiques, Shopify Plus confirmé Dandoy |
| 19 août | `87b03bd` | Fix noms de colonnes CSV redirections pour Matrixify |
| 6 août | `7f49fad` | Doc analyse migration gift cards (841 cartes, 281 actives, 9 247,49 €) |
| 5 août | `aa141a4` | Marquage commandes invoiced non expédiées comme refunded (règle client) |
| 5 août | `86d6e89` | Doc fix Fulfillment Line cartes cadeau |
| 30 juillet | `6e39f86` | Fix noms de colonnes Matrixify Orders — confirmé fonctionnel par tests réels |
| 30 juillet | `25986a0` | Mapping adresses billing/shipping (colonnes ajoutées à l'export Magento) |
| 30 juillet | `3ddbbd2` | Ajout samples clients et commandes pour tests Matrixify |
| 30 juillet | `7993a42` | Scripts adaptés pour générer les fichiers par boutique (Option B) |
| 30 juillet | `6f8fc7d` | Repasse documentaire complète pour l'architecture deux boutiques |
| 10 juillet | `047837f` | Suivi avancement mis à jour au 10 juillet 2026 |
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
| 26 juin | `b857ed5` | Plan de migration 5 phases (doc MkDocs) |
| 26 juin | `cc4b4ae` | Command: MERGE dans tous les scripts (réimport sécurisé) |
| 26 juin | `7dfed4d` | Suppression références export-orders.csv (pivot vers 2025-2026) |
| 26 juin | `bba429c` | Script conversion commandes + doc orders mise à jour |
| 25 juin | `ee2860a` | Page documentation historique commandes |
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
