# Journal de migration — Historique détaillé

> Ce journal complète [Avancement](./avancement.md), qui reste la page de référence pour
> l'état actuel (fichiers prêts, décisions en attente, reste à faire). Ici : le récit
> chronologique complet et l'historique des commits — utile pour retrouver le contexte
> d'une décision passée, pas pour un suivi rapide de l'état du projet.

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
  connus), découverte de 282 Titles Butterfly en néerlandais (voir correction du 20 août
  ci-dessous — ce n'était finalement pas un problème), fix de l'import des collections
  (mauvais en-tête de règle Matrixify), et intégration + correctif du block Custom options
  sur le thème Horizon (champs hors formulaire).

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

- Revue systématique des 18 pages MkDocs (à l'époque) pour éliminer toute référence
  résiduelle à l'Option A ou aux anciens noms de fichiers mono-boutique
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
  avancement.md) : recherche de la doc officielle Matrixify (contredit partiellement une
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

### Échantillon stratifié 950 commandes + bug adresse + statut refunded (4–5 août 2026)

- **`build_orders_stratified_sample.py` ajouté** : contrairement à l'échantillon de 5 commandes,
  tire ~40-100 commandes par cas limite (conversion devise, paiement `pending`, expédition
  partielle `Invoiced`/`Mixed`, grosses commandes ≥10 articles, point relais Sendcloud) + tous
  les stores et passerelles de paiement, plafonné à 950 commandes.
- **Bug `clean_street()` trouvé et corrigé** lors du 1er test live (23 échecs "Address 1 vide") :
  le filtre anti-duplication de ville supprimait à tort des adresses mono-ligne valides. 58 cas
  au total corrigés sur les 39 094 commandes ; ~14-15 restent réellement vides côté Magento
  (ville tapée dans le champ rue).
- **Statut "non traité" des commandes `Invoiced`-only investigué** : 318 commandes concernées,
  dont 216 (68 %) sont des chèques cadeau (jamais `Shipped` par nature) et 102 (32 %) des
  produits physiques. **Explication du client : ce sont des commandes remboursées/annulées**
  côté client final (règle métier non stockée dans Magento). Règle implémentée dans
  `magento_to_shopify_orders.py` (`is_unshipped_refund()`) : `Payment: Status = refunded` pour
  toute commande 100 % `Invoiced`/non-`Shipped`, hors cartes cadeau. 102 commandes concernées
  (39 Dandoy + 63 Butterfly), testées en live sur 33/102 via l'échantillon stratifié — comportement
  confirmé correct. **Décision client : archivage manuel** des 102 commandes après import
  (Matrixify ne permet pas de créer-et-archiver en un seul import).
- **Cartes cadeau marquées comme traitées** : `product_type = mageworx_giftcards` (4 SKU) →
  221 `Fulfillment Line` supplémentaires générées (216 commandes 100 % cartes cadeau + 5
  commandes mixtes physique/carte cadeau).

### Redirections — fix colonnes Matrixify + audit URLs localisées (6–10 août 2026)

- **6 août** : Matrixify rejetait le CSV de redirections (`"Cannot understand the uploaded
  file"`) — en-têtes `Redirect From`/`Redirect To` non reconnus, corrigés vers le vrai template
  (`ID`, `Path`, `Command`, `Target`).
- **10 août** : audit des URLs produits dont l'`url_key` diffère entre la vue de base et la vue
  store localisée (FR/NL) — **125 URLs Butterfly FR** (`be.butterfly.tt`) non couvertes par le
  script actuel (qui ne génère qu'à partir de l'`url_key` de base), NL quasi pas concerné (0
  partout). De même, les redirections de catégories restent en anglais uniquement — aucune
  colonne `categories` renseignée sur les vues FR/NL dans l'export Magento. **Décision : les
  deux trous se traitent manuellement** dans Shopify Admin après import, pas d'extension de
  script prévue — voir [Redirections 301](./import/redirections.md).

### Remises club & B2B — Companies (13–19 août 2026)

- **13 août** : analyse des 93 groupes clients Magento (84 utilisés) + 88 Cart Price Rules de
  remise club permanente (sans coupon), révélant que les remises sont **segmentées par famille
  de produits** (pas un taux plat par club) — 6 paliers de remise distincts entre les deux
  marques. Décision : **Companies B2B sur les deux boutiques** (Shopify a ouvert le B2B à tous
  les plans depuis avril 2026, pas seulement Plus).
- **19 août — deux corrections importantes** :
  - **Shopify Plus confirmé pour Dandoy-Sports** (catalogues B2B illimités) ; Butterfly reste en
    Basic (limite de **3 catalogues actifs**).
  - **Erreur de calcul corrigée** : les 3 règles Butterfly Premium (15 %/5 %/7 %) portent sur des
    **familles de produits différentes**, pas un taux combiné unique — Butterfly a donc besoin de
    **4 catalogs**, pas 3, ce qui **dépasse la limite Basic**. Décision à prendre avec le client
    (fusionner 2 catalogs ou upgrade de plan).
  - Confirmé : Matrixify **ne peut pas créer de Catalog** (nom/remise/contenu) — création
    manuelle obligatoire dans Shopify Admin ; le contenu par catégorie doit être fourni comme
    liste explicite de SKU (`Included / <Catalog>` sur le sheet Products, chantier séparé non
    encore scripté).
  - Les **2 Catalogs Dandoy créés** (`Dandoy — Club 20%`, `Dandoy — Club 15%`) ; colonne
    Matrixify `Location: Catalogs` confirmée fonctionner avec le nom du catalog.
  - **`generate_companies.py` ajouté** et câblé dans `regenerate_all.sh` (étape 5/9, Dandoy
    uniquement) : `shopify_companies_dandoy.csv` généré (85 companies, 2 086 lignes) — adresse et
    contact principal omis par décision client (complément manuel post-migration).
  - Détail complet : [Remises club & B2B](./mapping/club-b2b.md).

### Migration des chèques cadeaux — Option B, API, test live confirmé (5–20 août 2026)

- **5 août** : export `gift_cards_export_file.csv` analysé — 841 cartes, **281 actives**
  (9 247,49 €) à migrer. Deux méthodes de migration comparées (Matrixify/Orders — génère de
  nouveaux codes — vs API `giftCardCreate` — préserve les codes existants) : **Option B (API)
  retenue** pour éviter de recontacter les 281 titulaires.
- **App API `Migration Tooling — Magento2Shopify`** créée et installée sur Dandoy-Sports (via
  Dev Dashboard, org Partner Quai31) — scopes Cartes-cadeaux/Réductions/Clients accordés.
- **Obtention du token, plusieurs impasses avant la bonne méthode** : le Client Credentials
  Grant (le plus simple) échoue systématiquement (`shop_not_permitted`) sur une boutique
  payante — restriction Shopify volontaire, réservée aux boutiques de développement. Bascule
  vers l'**Authorization Code Grant**, qui nécessite un serveur de callback ; écrit
  `get_shopify_access_token.py` (serveur local temporaire, token écrit directement dans un
  fichier d'environnement non versionné, jamais affiché en clair) — token permanent obtenu
  avec succès le 20 août.
- **Test réel confirmé le 20 août** : 1 carte cadeau créée avec succès (code Magento préservé,
  solde correct, `enabled: true` côté API) — non visible immédiatement dans l'Admin car le code
  y est masqué par défaut, confirmé exister via requête API directe.
- **Liaison automatique au compte client ajoutée** (`migrate_giftcards_shopify.py` recherche le
  client Shopify par email et attache `customerId`) — nécessite l'import complet des clients au
  préalable (la boutique de test n'en contient que 563 sur 33 357 attendus, donc aucun match
  pour l'instant).
- Détail complet : [Chèques cadeaux](./import/gift-cards.md), [Identifiants API](./import/api-credentials.md).

### Audit documentaire approfondi (20 août 2026)

Relecture complète du site MkDocs (22 pages) suite à deux semaines de travail non tracées
dans le suivi d'avancement (voir sections Companies/gift cards/redirections ci-dessus) :

- **Vérification systématique des liens internes** : aucun lien cassé sur les 22 pages.
- **Recalcul de tous les chiffres** depuis les CSV actuels plutôt que recopiés d'anciennes
  versions — corrections trouvées : compteur de commandes obsolète dans
  `contraintes-techniques.md` (23 823/13 607 → 24 896/14 198, dérive due aux Fulfillment
  Lines ajoutées depuis), étape Companies B2B totalement absente de `quick-start.md`
  (ajoutée en étape 5, renumérotation 6→9), nombre de pages MkDocs (15→22).
- **Ajout de deux contraintes techniques jamais documentées** dans
  `contraintes-techniques.md` : la limite de catalogues B2B Butterfly (confirmée bloquante)
  et l'absence de tout chemin CSV Matrixify pour gift cards/codes promo (API obligatoire).
- **Vérification des 3 points "à faire" les plus anciens du suivi** :
  - **36 doublons de variantes** : confirmés inchangés en relançant `validate_shopify_csv.py`
    sur les CSV actuels — 32 produits distincts touchés (0,6 % du catalogue), erreur
    bloquante mais localisée à la ligne (le reste du produit s'importe quand même).
  - **282 Titles Butterfly en néerlandais** : **retiré, c'était une fausse alerte.**
    L'hypothèse d'origine (`(base)` = anglais partout) était fausse — le client a confirmé
    que le **néerlandais est la langue par défaut de la boutique Shopify Butterfly**, et un
    échantillon montre que 100 % des SKU Butterfly (pas seulement les 282 signalés) ont déjà
    leur Title de base en néerlandais. Invalide au passage la recommandation "prioriser la
    traduction NL post-migration" dans `langues.md` (couverture réelle quasi complète, pas
    2 %). Aucun changement de script nécessaire — l'erreur était uniquement documentaire.
  - **88 clubs vs 85 companies générées** : expliqué, pas un bug — `generate_companies.py`
    filtre sur `brand == 'Dandoy'` (sortie Dandoy uniquement), et 3 des 88 clubs n'ont une
    remise que côté Butterfly, donc absents à juste titre de `shopify_companies_dandoy.csv`.
- **Restructuration de cette page elle-même** : `avancement.md` (677 lignes) scindé en deux —
  état actuel (fichiers prêts, décisions, reste à faire) d'un côté, journal chronologique +
  historique des commits de l'autre (cette page). Le mirror interne
  `02_ANALYSIS_AND_MAPPING/avancement_migration.md`, qui avait déjà causé une dérive
  documentaire une fois (voir "Audit documentaire approfondi" ci-dessus), est supprimé —
  une seule version canonique désormais, celle du site MkDocs.
- Détail complet : [Contraintes techniques](./contraintes-techniques.md),
  [Gestion des langues](./architecture/langues.md), [Remises club & B2B](./mapping/club-b2b.md).

### 1ère synchro complète clients/commandes + fix qualité données (21 août 2026)

Premier import Matrixify réel sur le fichier clients complet (33 770 clients, contre 563 sur
la boutique de test jusque-là) — la stratégie en 2 passes du 20 août ([Plan de
migration](./import/plan-migration.md)) démarre officiellement. Deux campagnes de test live
successives ont mis au jour des problèmes de qualité de données jamais visibles sur les petits
échantillons testés jusqu'ici :

- **1er import (13 588 échecs / 33 770 clients, 40 %)** : `Phone is invalid` (1 949+),
  `Province is invalid`, `"Address: Country Code" is not valid`, `First/Last name cannot
  contain URL` — Magento n'a jamais imposé de format sur téléphone/région/nom, Shopify/
  Matrixify si. Root-caused et corrigé dans `magento_to_shopify_customers.py` :
  - Téléphones normalisés en E.164 via la lib `phonenumbers` (nouvelle dépendance externe,
    la première du pipeline — jusque-là 100 % stdlib Python).
  - Province envoyée uniquement pour les adresses avec un `region_id` Magento réel (pas de
    texte libre placeholder).
  - Pays non vendables par Shopify (`AN`, `AQ`, `TF`, `HM`…) : adresse ignorée.
  - 2 919 comptes bot historiques (spam/liens dans les champs nom) détectés et exclus
    entièrement du CSV.
- **2e import (231 échecs / 30 941, 0,75 %)** : régression du 1er round de correction —
  ma détection "province si `region_id` réel" ne suffisait pas (Shopify n'a **aucune** liste
  de provinces pour la Belgique/Pays-Bas/Luxembourg, même avec un vrai `region_id`), et des
  pays réels mais mal orthographiés côté Magento (`Bucureşti`, `Aiti` pour Aichi, `Yukon
  Territory` au lieu de `Yukon`) échouaient aussi pour d'autres pays (Roumanie, Japon, Canada,
  Mexique, Pérou). Décision (validée avec le client) : **Province envoyée uniquement pour les
  US**, seul pays sans aucun échec observé sur les deux campagnes — partout ailleurs, vidée
  plutôt que de parier sur la correspondance exacte avec la liste Shopify. Complété par :
  `PR`/`GU`/`AS` ajoutés aux pays non supportés (Shopify les traite comme des états US, pas
  des pays), troncature `Address1` à 255 caractères (limite Matrixify), et un filtre sur les
  indicatifs téléphoniques non-géographiques (ex. `+979`) que `phonenumbers` validait à tort.
- **Limitation résiduelle documentée, non corrigeable depuis le CSV seul** : 15
  `Phone has already been taken` — deux comptes différents partageant un numéro déjà présent
  côté Shopify suite à l'import Phase 1 ; indétectable sans interroger l'API Shopify live.
- Même nettoyage appliqué à `magento_to_shopify_orders.py` (adresses billing/shipping) en
  réutilisant les mêmes fonctions plutôt que de dupliquer la logique — 24 commandes avec un
  pays non supporté en billing **et** shipping (23× `TF`, 1× `AQ`) laissées telles quelles et
  signalées à l'exécution, faute de pouvoir deviner un remplacement fiable.
- Les 4 règles (téléphone, province, pays, nom spam) ajoutées à `validate_shopify_csv.py`
  pour qu'un futur export Magento qui réintroduirait les mêmes problèmes soit détecté
  automatiquement à la régénération, sans attendre un nouvel import Matrixify réel.
- Détail complet : [Migration clients](./import/customers.md#nettoyage-des-données-téléphone-province-pays-noms),
  [Historique des commandes](./import/orders.md#nettoyage-des-adresses-téléphone-province-pays).

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
| 19 août | `058749e` | Capture Admin Magento règle 3983 (conditions) |
| 19 août | `6831b72` | Correction club-b2b.md : Butterfly a besoin de 4 catalogs, pas 3 |
| 19 août | `b34b477` | Correction cumul remises club + tous les rule_id Cart Price Rule documentés |
| 19 août | `5388420` | Doc stratégie Companies B2B deux boutiques, Shopify Plus confirmé Dandoy |
| 19 août | `12803fc` | `custom.blade_layers` et configuration metafields marqués faits |
| 19 août | `87b03bd` | Fix noms de colonnes CSV redirections pour Matrixify |
| 6 août | `7f49fad` | Doc analyse migration gift cards (841 cartes, 281 actives, 9 247,49 €) |
| 5 août | `39b9b21` | Note : archivage manuel des 102 commandes remboursées par le client |
| 5 août | `3ebac35` | Doc investigation archivage/annulation commandes remboursées |
| 5 août | `9e3eeb7` | Note couverture test live de la règle refunded (33/102) |
| 5 août | `203b219` | Doc règle refunded, correction demande colonne export |
| 5 août | `aa141a4` | Marquage commandes invoiced non expédiées comme refunded (règle client) |
| 5 août | `0ef3dd0` | Doc explication client : 102 commandes physiques = annulations remboursées |
| 5 août | `86d6e89` | Doc fix Fulfillment Line cartes cadeau |
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
| 10 juillet | `2bdc8e8` | Doc 282 Titles Butterfly en néerlandais (traduction EN manquante — voir correction 20 août) |
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
