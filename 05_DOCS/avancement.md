# Avancement Migration Magento → Shopify — Dandoy-Sports / Butterfly TT

Dernière mise à jour : **5 août 2026**

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
| `shopify_orders_dandoy.csv` / `_butterfly.csv` | 74 535 / 30 027 | 24 855 / 14 196 commandes avec line items (39 051 au total, période complète jan. 2025 → aujourd'hui) |
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

Après mise à jour de l'export Magento :

```bash
bash 02_ANALYSIS_AND_MAPPING/SCRIPTS/regenerate_all.sh
```

8 étapes : produits + traductions → collections → redirections → customers → commandes →
sample → purge → validation, chacune générant les fichiers des deux boutiques.

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

### Repasse documentaire complète + samples clients/commandes (30 juillet 2026)

- Revue systématique des 18 pages MkDocs + leurs mirrors `02_ANALYSIS_AND_MAPPING/` pour
  éliminer toute référence résiduelle à l'Option A ou aux anciens noms de fichiers mono-boutique
  (`multi-sites.md`, `langues.md`, `redirections.md`, `orders.md`, `customers.md`,
  `plan-migration.md`, `quick-start.md`, `contraintes-techniques.md`, `custom-options.md`,
  `bundles.md`, README/CLAUDE/GUIDE_PRESTATAIRE)
- Corrections indépendantes trouvées au passage : lien cassé `quick-start.md` →
  `mapping/metafields.md` (page scindée depuis), typo d'en-tête dans `contraintes-techniques.md`,
  comptage obsolète 19→20 metafields (`custom.available_options` manquant), `custom_options_shopify.md`
  très en retard sur sa version 05_DOCS
- `regenerate_all.sh` génère désormais aussi des échantillons clients (10/boutique, 5 avec
  adresse + 5 sans) et commandes (5 commandes complètes/boutique, avec line items) — versionnés
  comme le sample produits, à la demande du client malgré les données personnelles réelles qu'ils
  contiennent en petite quantité

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
  suggestion externe — colonnes `Fulfillment: Status/Date/Send Receipt` proposées directement
  sur les lignes `Line Item`, alors que Matrixify exige une ligne séparée
  `Line: Type = 'Fulfillment Line'`, confirmé par leur documentation officielle). 99,2 % des
  commandes (38 722/39 051) ont tous leurs items à `Status = Shipped` → une ligne
  Fulfillment par commande (`Fulfillment: Status = success`, `Fulfillment: Send Receipt =
  FALSE` pour ne pas ré-notifier les clients) ; les 0,8 % restants (statuts Invoiced/Mixed)
  restent non expédiés plutôt que de deviner un état.
- **Date d'expédition (`Fulfillment: Processed At`)** : aucune date fiable disponible côté
  export Magento à ce stade. Écarté `Bpost Drop/Delivery Date` (ne couvre que 18 % des
  commandes — bpost est loin d'être le seul transporteur) et `Created At` (date de commande,
  pas d'expédition). Décidé de demander l'ajout de `Updated At` à l'export Magento (couvre
  100 % des commandes, approximatif mais mieux que rien).
- **Champ `Note` identifié comme utile** : pourrait porter le point relais (bpost/DPD/
  Sendcloud) et l'ID de transaction Mollie — colonnes disponibles côté attributs Magento
  (`mollie_transaction_id`, `bpost_point_*`, `dpd_parcelshop_*`, `sendcloud_service_point_*`)
  mais absentes de l'export actuel — à demander en même temps que `Updated At`.
- **PayPlug/PayPal Express/Klarna** : aucun ID de transaction dans la liste d'attributs order
  Magento Admin (confirmé — le prestataire/dev Magento du projet a vérifié directement).
  Probablement stocké hors des attributs order plats
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

### Test live Fulfillment Line : 2 échecs, correction, puis validation (4 août 2026)

Premier test réel du mécanisme Fulfillment Line sur le sample commandes (`Import_Result_
2026-08-04_105413`) : **échec des 5 commandes**, toutes avec la même erreur — `Error saving
Fulfillment: Cannot find Line Item [N] to fulfill`, où `N` est l'ID que le script avait
attribué à la ligne `Fulfillment Line` elle-même (8, 10, 18, 23, 28). Cause : donner un
`Line: ID` neuf à la ligne `Fulfillment Line` fait que Matrixify la traite comme un
fulfillment **partiel** référençant ce `Line Item` précis — qui n'existe pas puisque les
vrais items de la commande ont des ID différents (1 à 7 par ex.). Il fallait laisser
`Line: ID` **vide** sur ces lignes pour déclencher un fulfillment complet de la commande.

**2ᵉ test** (`Import_Result_2026-08-04_110302`, après le fix ci-dessus) : erreur `Cannot find
Line Item` disparue, mais nouvelle erreur — `You have set the "Fulfillment: Processed At"
date - therefore you also need to set the "Fulfillment: Shipment Status" of: "delivered" or
"failure".` Ajouté `Fulfillment: Shipment Status = 'delivered'` (commandes historiques déjà
expédiées).

**3ᵉ test confirmé fonctionnel** (`shopify-cmd-exemple.png`, commande WEB1-0125-17658) : statut
"Traitée" + "Livré le mercredi 15 janvier 2025" (correspond à `Fulfillment: Processed At =
2025-01-15 09:55:04`), `Note` affichée correctement (`Mollie: tr_z3dhtPdFyW`), taxe et remise
conformes (VAT 21% = 18,82€, réduction -9,96€). Écart d'1 centime observé sur le Total affiché
(108,46€ vs 108,45€ attendu/Magento) — probablement un arrondi d'affichage Shopify recalculant
à partir des composants plutôt que d'utiliser `Price: Total` tel quel ; non bloquant, à
surveiller si ça se reproduit à plus grande échelle.

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
| [Historique des commandes](./import/orders.md) | Script conversion, fiscalité, Fulfillment Line, champ Note, liaisons clients, import Matrixify |
| [Plan de migration](./import/plan-migration.md) | Plan 5 phases : foundation → theming → recette → pré-go-live → go-live |
| [Chèques cadeaux](./import/gift-cards.md) | Analyse export 841 cartes, 281 actives (9 247,49 €), 2 méthodes de migration — à faire |

---

## Décisions en attente

| Sujet | Options | Décision | Impact |
|---|---|---|---|
| **Multi-sites** | A : instance unique + Markets / B : deux boutiques | **Option B retenue (29 juillet 2026)** — deux boutiques, Butterfly en plan Basic | Scripts adaptés — voir ci-dessus |
| **Custom options** | Line item properties / App tierce | **Line item properties** (natif, gratuit) | Code thème à ajouter |
| **Livraison tables** (33 produits) | App tierce / Variante Shopify | **App tierce** (prix variables 41–116 €) | Coût mensuel |
| **Plan Basic Butterfly** | — | À valider | Limitations à vérifier (rapports pro, shipping tiers calculé, comptes staff) |
| **Fulfillment des commandes migrées** | Fulfillment Line rows / accepter "non expédiées" | **Fulfillment Line retenu et validé en live** (4 août 2026) — 2 échecs corrigés, 3ᵉ test confirmé fonctionnel (commande WEB1-0125-17658 : "Traitée", "Livré le 15 janvier 2025") | Terminé |

---

## Reste à faire

| Sujet | Priorité | Statut |
|---|---|---|
| Plan de migration | ~~À faire~~ | **Fait** — 5 phases documentées ([Plan de migration](./import/plan-migration.md)) |
| Décision multi-sites (A ou B) | ~~Haute~~ | **Fait** — Option B retenue, scripts adaptés (29-30 juillet 2026) |
| Import test complet Matrixify (produits) | ~~Haute~~ | **Fait** — 272/25 514 échecs, tous identifiés (voir ci-dessus, sur l'ancien catalogue unique — à retester par boutique) |
| Import test commandes Matrixify | ~~Haute~~ | **Fait** — sample confirmé fonctionnel après 5 corrections (colonnes, adresses, line items — voir ci-dessus) |
| 36 doublons de variantes (données Magento) | **Haute** | À corriger manuellement — [Doublons de variantes](./mapping/doublons-variantes.md) |
| 282 Titles Butterfly en néerlandais | **Haute** | Traduction EN manquante — action requise côté Butterfly avant go-live |
| Vérifier limitations plan Basic (Butterfly) | **Haute** | À faire avant validation finale de l'Option B |
| Ajouter `Updated At` + point relais (bpost/DPD/Sendcloud) + `mollie_transaction_id` à l'export Magento | ~~Haute~~ | **Fait** (4 août 2026) — export mis à jour, mappé dans le script (`Fulfillment: Processed At` + champ `Note`) |
| Vérifier en base (`sales_order_payment.additional_information`) si un ID de transaction existe pour PayPlug, PayPal Express et Klarna (~2 850 commandes, 7,3%) — **confirmé absent** de la liste d'attributs order Magento Admin | Moyenne | À vérifier directement en base — à défaut, `Note` restera vide pour ces commandes |
| Tester en live le mécanisme Fulfillment Line (commandes) | ~~Haute~~ | **Fait** — 2 échecs corrigés le 4 août 2026, 3ᵉ test confirmé |
| `custom.blade_layers = "4"` refusé (7 produits Tibhar) | ~~Moyenne~~ | **Fait** — valeur ajoutée aux choix prédéfinis dans l'Admin Shopify |
| Configuration metafields (choix prédéfinis) | ~~Moyenne~~ | **Fait** — metafields configurés dans l'Admin Shopify |
| Configuration Search & Discovery (filtres) | Moyenne | Documenté — Phase 1 |
| Migration clients | ~~À évaluer~~ | **Fait** — `shopify_customers_{dandoy\|butterfly}.csv` prêts (33 357 / 11 404 clients), sample testé OK |
| Migration commandes | ~~À évaluer~~ | **Fait** — `shopify_orders_{dandoy\|butterfly}.csv` prêts (24 855 / 14 196 commandes), sample testé OK |
| Plan Matrixify | ~~À évaluer~~ | **Enterprise ($200/mois)** — 1 mois, puis Basic |
| Stock Sync (config SFTP + mapping SKU) | **Haute** | **Documenté** — guide prestataire prêt (Phase 2), à dupliquer sur les 2 boutiques |
| Bundle products (105) | ~~Moyenne~~ | **Documenté** — remises auto Shopify (Phase 2) |
| Migration chèques cadeaux (281 cartes actives, 9 247,49 €) | **Haute** | **À faire** — analyse faite, méthode à décider ([Chèques cadeaux](./import/gift-cards.md)) |
| Pages CMS Magento | Basse | Non commencé (Phase 2) |
| Thème Shopify + branding Butterfly | Hors périmètre data | Phase 2 — 2 thèmes à prévoir (Option B) |

---

## Historique des commits

| Date | Commit | Description |
|---|---|---|
| 4 août | `678d1bd` | Ajout génération PURGE commandes (DELETE en masse, pas Cancel) |
| 4 août | `3f46076` | Confirmation mécanisme Fulfillment Line validé en test live |
| 4 août | `9ee4251` | Doc 2e échec test live Fulfillment Line + correction |
| 4 août | `defcf28` | Ajout `Fulfillment: Shipment Status` requis avec `Processed At` |
| 4 août | `8f98a11` | Doc 1er échec test live Fulfillment Line + correction |
| 4 août | `18721ee` | Fix Fulfillment Line : `Line: ID` doit rester vide |
| 4 août | `653e03b` | Doc Fulfillment/Note débloqués, chiffres commandes rafraîchis |
| 4 août | `2cb5844` | Câblage `Updated At`, point relais et transaction Mollie dans le script |
| 4 août | `abe5128` | Correction : vérification en base = action du prestataire Magento (l'utilisateur), pas d'un tiers |
| 4 août | `1162948` | Confirmation absence transaction ID PayPlug/PayPal Express/Klarna |
| 4 août | `aa5683c` | Ajout question ouverte mapping transaction PayPlug/PayPal Express |
| 4 août | `9feb5d0` | Repasse doc en ligne commandes : chiffres, colonnes confirmées, fiscalité/fulfillment/note |
| 4 août | `dce46c1` | Doc fixes commandes du jour, décision Fulfillment Line, idée champ Note |
| 4 août | `93e8b7e` | Ajout mécanisme Fulfillment Line pour commandes expédiées |
| 4 août | `fa82347` | Ajout capture test Matrixify commande WEB1-0125-17658 |
| 3 août | `4197493` | Fix gestion taxes/remise/devise commandes (import Matrixify) |
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
