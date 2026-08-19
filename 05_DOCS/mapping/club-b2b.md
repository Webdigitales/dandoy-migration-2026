# Remises club & B2B

Magento gère un réseau de clubs de tennis de table partenaires via des **Customer Groups**
(un groupe par club) combinés à des **Cart Price Rules** (remises permanentes, sans coupon).
Ce document fait le pont entre ce système existant et les capacités **B2B (Companies)** de
Shopify.

> **Décision (13 août 2026) : Companies B2B sur les deux boutiques** (Dandoy-Sports ET
> Butterfly TT). Depuis avril 2026, Shopify a ouvert le B2B à tous les plans (pas seulement
> Plus) — Basic inclus, avec une limite de 3 catalogues actifs. Voir [§2](#2-équivalent-shopify)
> pour le détail et le raisonnement.

> Contexte : ce document intègre une piste de réflexion transmise par le client
> (`02_ANALYSIS_AND_MAPPING/DOC/Réflexion club-membres-remises.docx`), issue de ses propres
> recherches assistées par IA. Il ne s'agit pas d'une spec figée — certains points restent
> à valider avec le client (voir [Ouvert](#ouvert-à-valider-avec-le-client)).

---

## 1. Ce qui existe aujourd'hui dans Magento

Sources : `01_DATA_RAW/export_customer.csv` (`group_id`), `01_DATA_RAW/customer_group.csv`
(nom du groupe), `01_DATA_RAW/cart_price_rules.csv` (règles de remise).

- **93 groupes clients définis**, dont **84 réellement utilisés** (un client au moins).
- **Groupe `1 = General`** : 42 749 clients (92 %) — grand public, aucune remise permanente
  spécifique (seulement les paliers panier génériques, ex. `10% apd 100€`).
- **83 autres groupes = un club chacun** (ex. `14 = TT Progress`, 414 clients ;
  `54 = CTT ALPA`, 262 clients ; jusqu'à 1 seul client pour les plus petits clubs).
- **88 des 93 groupes ont une remise club permanente, automatique** (Cart Price Rule
  `coupon_type=1`, sans code, sans date de fin) :

| Règle Magento | Taux | Catégories couvertes | Exclusions SKU | Portée | # clubs |
|---|---|---|---|---|---|
| `Remises club 20% - Dandoy` | 20 % | Rubbers, Blades, Rackets, Clothing, Shoes, Luggages, Padel | 28 | Dandoy | 41 |
| `Remises club 15% - Dandoy` | 15 % | Rubbers, Blades, Rackets, Clothing, Shoes, Luggages, Padel | 28 | Dandoy | 44 |
| `Remises club 15% - Butterfly` | 15 % | Clothing, Shoes, Luggages | 0 | Butterfly | 49 (dont 5 cumulent aussi 5 % + 7 %, voir ci-dessous) |
| `Remises club 10% - Butterfly` | 10 % | Clothing, Shoes, Luggages | 0 | Butterfly | 27 |
| `Remises club 7% - Butterfly` | 7 % | Robots | 0 | Butterfly | 5 (groupes 20/88/89/93/95 — `website_id=4`/BE uniquement, pas NL) |
| `Remises club 5% - Butterfly` | 5 % | Rubbers, Blades, Glue, Cleaners | 5 | Butterfly | 5 (mêmes 5 clubs que ci-dessus) |
| `Remise club 5% addition STIGA` | 6,25 % | Rubbers, Blades, Clothing, Shoes, Luggages, Padel | 0 | Dandoy | 2 (groupes 29, 62) |
| `Sofiane Boukoula` | 30 % | Rubbers, Blades, Rackets, Clothing, Shoes, Luggages, Padel | 0 | Nominatif (Dandoy) | 1 client |

**Points clés :**
- Le taux **diffère selon la marque** pour un même club (17 clubs ont un taux Dandoy ET
  un taux Butterfly différents) — cohérent avec Option B (deux boutiques séparées).
- Ces remises club **s'additionnent** aux paliers panier génériques (`5% apd 50€`, etc.,
  eux aussi permanents et automatiques) — ce qui explique le taux de remise moyen assez
  homogène (~20-27 %) observé en analysant `export_order_all_2025_2026.csv` par groupe.
- **Aucune règle club n'est une remise plate sur tout le panier.** Chacune restreint son
  action à des catégories précises (`category_ids` dans `actions_serialized`), et les deux
  règles Dandoy (`3983`, `4048`) excluent en plus 28 SKU parents spécifiques. Vérifié via
  jointure avec `01_DATA_RAW/catalog_category.csv` (export `catalog_category_entity` +
  attribut `name`).
- **Butterfly est fortement segmenté par catégorie**, pas juste par taux : le tier
  15 %/10 % ne couvre QUE Clothing/Shoes/Luggages ; le "+5 %" des 5 clubs Premium ne
  s'applique QUE sur Rubbers/Blades/Glue/Cleaners ; le "+7 %" ne s'applique QUE sur Robots.
  **Ce ne sont pas 3 taux qui se cumulent en un seul pourcentage — ce sont 3 remises
  indépendantes sur 3 familles de produits différentes**, actives simultanément sur la même
  commande mais jamais sur les mêmes lignes. (Correction par rapport à une estimation
  précédente qui parlait à tort d'un taux combiné ~24,9 % sur tout le panier.)
- Dandoy est plus généraliste (7 catégories, presque tout le catalogue produit) avec
  seulement des exclusions SKU ponctuelles — pas de segmentation par famille comme
  Butterfly.
- Aucune donnée de **tier price par produit** (`catalog_product_entity_tier_price`) n'a
  été trouvée dans l'export produits — les remises sont uniquement au niveau panier/%,
  pas de grille tarifaire produit par produit à ce stade.
- Deux cas hors norme, à traiter à part (pas de catalog dédié standard) : **STIGA addition**
  (groupes 29, 62 — +6,25 % uniquement sur les produits STIGA, en plus du 20 % Dandoy) et
  **Sofiane Boukoula** (groupe 10 — 30 % nominatif, Dandoy uniquement ; ce même client a un
  taux standard 15 % côté Butterfly).

### Référence — rule_id des 8 règles club

| rule_id | Nom | Catégories | Catalog Shopify cible |
|---|---|---|---|
| `3983` | Remises club 15% - Dandoy | Rubbers/Blades/Rackets/Clothing/Shoes/Luggages/Padel | `Dandoy — Club 15%` |
| `4048` | Remises club 20% - Dandoy | Rubbers/Blades/Rackets/Clothing/Shoes/Luggages/Padel | `Dandoy — Club 20%` |
| `4049` | Remises club 15% - Butterfly | Clothing/Shoes/Luggages | `Butterfly — Clothing/Shoes/Luggages 15%` |
| `4226` | Remises club 10% - Butterfly | Clothing/Shoes/Luggages | `Butterfly — Clothing/Shoes/Luggages 10%` |
| `7969` | Remises club 5% - Butterfly | Rubbers/Blades/Glue/Cleaners | `Butterfly — Rubbers/Blades/Glue/Cleaners 5%` |
| `7970` | Remises club 7% - Butterfly | Robots | `Butterfly — Robots 7%` |
| `5331` | Remise club 5% addition STIGA | Rubbers/Blades/Clothing/Shoes/Luggages/Padel | cas particulier (hors catalog standard) |
| `5695` | Sofiane Boukoula | Rubbers/Blades/Rackets/Clothing/Shoes/Luggages/Padel | cas particulier (hors catalog standard) |

### Référence — paliers panier génériques (13 règles, tous plans/groupes confondus)

Toutes permanentes (`to_date=NULL`), `stop_rules_processing=1` sauf `26`.

**Série "ronde" (seuils TTC, groupes `0,1,2,3` = NOT LOGGED IN/General/Wholesale/Retailer) :**

| rule_id | Nom | Remise | Seuil panier |
|---|---|---|---|
| `16` | 5% apd 50€ | 5 % | ≥ 50,00 € et < 99,99 € |
| `17` | 10% apd de 100€ | 10 % | ≥ 100 € et < 149,99 € |
| `18` | 15% apd de 150€ | 15 % | ≥ 150 € et < 199,99 € |
| `19` | 20% apd de 200€ | 20 % | ≥ 200 € |
| `20` | 25% apd de 250€ | 25 % | ≥ 250 € |
| `21` | 30% apd de 300€ | 30 % | (condition subtotal non lisible dans l'export — probablement ≥ 300 €) |

**Série "62/99€" (seuils légèrement différents, mêmes groupes 0-3) :**

| rule_id | Nom | Remise | Seuil panier |
|---|---|---|---|
| `12` | 5% apd 75€ | 5 % | ≥ 61,98 € et < 99,17 € |
| `13` | 10% apd 120€ | 10 % | ≥ 99,18 € |

⚠️ Cette série (12-13, créée en 2021) recoupe des plages de montants proches de la série
"ronde" (16-17, créée en 2020) — les deux sont actives simultanément. Comme toutes ont
`stop_rules_processing=1`, une seule doit se déclencher par commande (priorité Magento non
disponible dans l'export reçu). Possible redondance de config héritée dans le temps plutôt
qu'un système à deux niveaux voulu — **à clarifier avec le client** avant de décider si les
deux séries doivent être répliquées sur Shopify ou une seule.

**Série "HT" (seuils différents, groupes `0,1,2,3,4` + la quasi-totalité des clubs) :**

| rule_id | Nom | Remise | Seuil panier | Groupes |
|---|---|---|---|---|
| `22` | 5% apd 50€ | 5 % | ≥ 41,32 € et < 82,64 € | 0,1,2,3,10 |
| `23` | 10% apd de 100€ | 10 % | ≥ 82,65 € et < 123,96 € | 0,1,2,3,4,10 |
| `24` | 15% apd de 150€ | 15 % | ≥ 123,97 € et < 165,29 € | 0,1,2,3 |
| `25` | 20% apd de 200€ | 20 % | ≥ 165,29 € et < 206,61 € | 0,1,2,3,4 + ~48 clubs |
| `26` | 25% apd de 250€ | 25 % | ≥ 206,61 € | 0,1,2,3,4 + ~92 clubs (`stop=0`) |

C'est cette série qui touche la majorité des clubs en plus de leur remise club — source du
cumul club + palier panier observé en analysant `export_order_all_2025_2026.csv`. `26` étant
la seule règle sans `stop_rules_processing`, elle peut légitimement s'empiler avec une remise
club (`3983`, `4048`, etc.) sur une même commande.

---

## 2. Équivalent Shopify

### Companies B2B — disponible sur les deux boutiques

Shopify a ouvert le B2B à **tous les plans depuis avril 2026** (Basic, Grow, Advanced, Plus),
pas seulement Plus. Ce qui est **identique sur tous les plans** (donc sur Dandoy-Sports
comme sur Butterfly TT) :

- Companies, Company locations, permissions par location
- Quantity rules & price breaks
- **Net payment terms** (Net 7 à Net 90)
- Draft orders & invoicing, PO numbers
- Quick order list, Shopify Flow automations

Ce qui **diffère selon le plan** :

| | Basic / Grow / Advanced (Butterfly) | Plus (Dandoy-Sports) |
|---|---|---|
| Catalogues B2B actifs | max **3** | illimité |
| Assignation directe catalogue → company/location | non (passe par les B2B markets) | oui |
| Deposits / paiements partiels / payment requests | non | oui |

| Besoin club | Fonctionnalité B2B Shopify |
|---|---|
| Remise permanente par club | **Price lists / Catalogs** liés à la Company (remise % ou prix fixe) |
| Club = plusieurs personnes autorisées (président, trésorier, entraîneur) | **Company locations** + **Company contacts**, rôles `Ordering only` / `Location admin` |
| Catalogue restreint par club (ex. balles par carton pour les clubs uniquement) | **Catalogs** attribués par Company |
| Paiement à échéance (30/60 jours) | **Net terms** (natif, tous plans) |
| Devis | **Draft orders** envoyés au client |
| Commande au nom d'un club par un commercial | **Shopify Admin → créer commande pour une Company** |

C'est un site **unique par boutique** qui sert à la fois les particuliers (boutique
grand public classique) et les clubs (comptes Company) — pas de conflit avec Option B,
qui porte sur le découpage Dandoy/Butterfly, pas sur particuliers/clubs.

### Pourquoi Companies plutôt que tags + segments + automatic discount

L'alternative "légère" (tag club à l'import, segment basé sur le tag, remise automatique
scopée sur le segment) a été écartée après comparaison :

- Elle ne modélise qu'**"appliquer X % à ce client"**, sans notion d'entité club — pas de
  regroupement multi-contact, pas d'historique d'achat agrégé par club.
- Le client a déjà exprimé l'envie d'aller plus loin (dotation annuelle, multi-utilisateurs
  par club, commande rapide par SKU — voir [§4](#4-ouvert--à-valider-avec-le-client)) :
  Companies donne ces briques nativement (locations = contacts multiples, historique agrégé
  par company = base du calcul de dotation, quick order list, PO numbers). Partir sur
  tags+segments maintenant serait du travail à refaire si le client valide ces pistes.
- Net terms et Companies sont natifs sur tous les plans désormais — l'argument "Basic ne
  peut pas" ne tient plus.
- ⚠️ **Correction (19 août 2026) : la limite de 3 catalogues actifs sur Butterfly (Basic)
  ne tient plus.** Le calcul précédent supposait un taux unique combiné (~24,9 %) pour les
  5 clubs Premium. Or les 3 règles concernées (15 %, 5 %, 7 %) portent sur des **familles de
  produits différentes** (Clothing/Shoes/Luggages, Rubbers/Blades/Glue/Cleaners, Robots) —
  pour une fidélité complète, Butterfly a besoin de **4 catalogs distincts**, pas 3
  (voir liste ci-dessous), ce qui **dépasse la limite Basic**. Décision à prendre avec le
  client (voir [§4](#4-ouvert--à-valider-avec-le-client)) : simplifier (fusionner
  Rubbers/Blades/Glue/Cleaners + Robots dans le catalog Clothing/Shoes/Luggages existant,
  au prix d'une perte de fidélité sur ces 5 clubs) ou passer ces 5 companies sur un plan
  supérieur.

### Liste des Catalogs à créer (mise à jour 19 août 2026)

| Boutique | Catalog | Remise | Catégories | # clubs | Statut |
|---|---|---|---|---|---|
| Dandoy-Sports | `Dandoy — Club 20%` | 20 % | Rubbers/Blades/Rackets/Clothing/Shoes/Luggages/Padel | 41 | ✅ Créé (19 août 2026) |
| Dandoy-Sports | `Dandoy — Club 15%` | 15 % | Rubbers/Blades/Rackets/Clothing/Shoes/Luggages/Padel | 44 | ✅ Créé (19 août 2026) |
| Butterfly TT | `Butterfly — Clothing/Shoes/Luggages 15%` | 15 % | Clothing, Shoes, Luggages | 49 | À créer — bloqué par la limite 3 catalogs |
| Butterfly TT | `Butterfly — Clothing/Shoes/Luggages 10%` | 10 % | Clothing, Shoes, Luggages | 27 | À créer — bloqué par la limite 3 catalogs |
| Butterfly TT | `Butterfly — Rubbers/Blades/Glue/Cleaners 5%` | 5 % | Rubbers, Blades, Glue, Cleaners | 5 | À créer — bloqué par la limite 3 catalogs |
| Butterfly TT | `Butterfly — Robots 7%` | 7 % | Robots | 5 | À créer — bloqué par la limite 3 catalogs |

**6 catalogs standards** (2 Dandoy + 4 Butterfly). Dandoy (Plus, illimité) n'a aucun
problème. **Butterfly (Basic, max 3) dépasse la limite avec 4 catalogs** — voir décision à
prendre en §4. Les deux cas particuliers (STIGA addition, compte nominatif Boukoula)
restent **hors de cette liste** — à trancher séparément.

### Import en masse via Matrixify

Matrixify supporte un sheet dédié **Companies**. Colonnes réelles vérifiées sur le fichier
demo officiel (`Matrixify-Import-Demo-Companies.xlsx`, 43 colonnes) :

- **Company** : `Name`, `Command`, `External ID`, `Notes`, `Customer Since`,
  `Main Contact: Customer ID`, `Main Contact: Customer Email`
- **Location** : `Location: Name/Command/External ID/Phone/Notes/Locale/Tax ID/
  Tax Exemptions`, `Allow Shipping To Any Address`, `Checkout To Draft`,
  `Checkout Payment Terms` (ex. `"Net 30"`), puis adresses **Shipping** et **Billing**
  complètes (`Recipient`, `Phone`, `Address 1/2`, `Zip`, `City`, `Province Code`,
  `Country Code`)
- **Contact lié** : `Customer: Email`, `Customer: Command`, `Customer: Location Role`
- **Store Credit** (non utilisé ici) : 6 colonnes

Commandes `NEW` / `MERGE` / `UPDATE` / `REPLACE` / `DELETE` — réimportable comme le reste
du pipeline.

**Prérequis strict : les clients doivent déjà exister dans Shopify avant l'import
Companies**, sinon échec (liaison par email ou ID). Implique l'ordre d'import :
`shopify_customers_*.csv` → `shopify_companies_*.csv`.

Aucune restriction de plan Matrixify spécifique aux Companies (Enterprise déjà prévu pour
le premier mois — largement suffisant pour 88 companies).

#### Catalogs — création manuelle obligatoire, contenu à générer

**Matrixify ne peut pas créer de Catalog** (nom, % de remise) — confirmé par le tutoriel
Matrixify sur le pricing produit par marché/catalog : la création se fait uniquement dans
Shopify Admin (Settings → B2B / Markets).

**Shopify n'offre par ailleurs aucun filtrage par collection/catégorie à la création d'un
Catalog** (vérifié le 19 août 2026 sur `help.shopify.com/en/manual/b2b/catalogs/creating-catalogs`)
— seulement deux options : **"All products"** ou **"Specific products"** (sélection
individuelle par recherche ou import CSV). Il n'y a pas d'équivalent "toutes les
collections Rubbers+Blades+..." en un clic.

**Conséquence :** le scoping par catégorie qu'on a décodé côté Magento (§1) ne se
configure pas au niveau du Catalog lui-même — il faut fournir à Matrixify la **liste
explicite des produits/SKU** à inclure dans chaque Catalog, via la colonne
`Included / <Catalog>` (et `Price / <Catalog>` si prix fixe) sur le sheet **Products**, pas
sur le sheet Companies. Ça implique un nouveau step de génération (probablement une
extension de `magento_to_shopify.py` ou un script dédié) qui :
1. Filtre `export_magento_products_all.csv` par la colonne `categories` (texte) pour
   retrouver les produits de chaque famille (Rubbers, Blades, Clothing, etc.) ;
2. Exclut les 28 SKU parents pour les deux catalogs Dandoy, et les 5 SKU pour
   `Butterfly — Rubbers/Blades/Glue/Cleaners 5%` ;
3. Ajoute une colonne `Included / <Catalog>` par catalog cible dans le CSV produits
   (Dandoy : 2 colonnes, Butterfly : jusqu'à 4).

Ce step est **indépendant de `generate_companies.py`** (qui ne gère que Companies/Locations/
Contacts) — à traiter comme une deuxième brique du même chantier, pas la même génération.

**Décision (14 août 2026) :** le client crée manuellement les Catalogs vides (un par palier
de remise × par boutique — 2 pour Dandoy, 4 pour Butterfly, voir §2) et fournit la table
`taux → nom du Catalog Shopify`. Le rattachement Company → Catalog se fait ensuite via la
colonne `Location: Catalogs`, dont la valeur est le **nom du catalog** (ex.
`Dandoy — Club 20%`) — **confirmé le 19 août 2026** dans l'app réelle (absente du fichier
demo statique inspecté plus tôt, mais bien présente en pratique).

Les **2 Catalogs Dandoy sont créés** (`Dandoy — Club 20%`, `Dandoy — Club 15%`, noms
suggérés repris tels quels). Butterfly reste bloqué par la limite de 3 catalogs (§2).

Deux nouveaux scripts sont donc à prévoir : `generate_companies.py` (Companies/Locations/
Contacts, depuis `club_discount_mapping.csv` + la table Catalogs fournie par le client) et
un step de génération du contenu produit par catalog (`Included / <Catalog>` sur le sheet
Products) — les deux à ajouter à `regenerate_all.sh` et à l'ordre d'import Matrixify de
`CLAUDE.md` (Companies après `shopify_customers_*.csv` ; le contenu des catalogs peut être
ajouté directement au CSV produits existant, avant `shopify_products_*.csv`).

---

## 3. Mapping des 88 clubs (group_id → nom → taux)

Généré dans `02_ANALYSIS_AND_MAPPING/club_discount_mapping.csv` (174 lignes — une ligne par
club × règle Magento, donc plusieurs lignes par club quand plusieurs règles s'appliquent, ex.
les 5 clubs Butterfly Premium ont 3 lignes) depuis `cart_price_rules.csv` +
`customer_group.csv` + `catalog_category.csv`. Colonnes : `group_id`, `club_name`, `brand`,
`discount_pct`, `magento_rule`, `rule_id`, `nb_clients`, `categories` (familles de produits
couvertes par la règle), `sku_exclusions` (nombre de SKU exclus), `catalog_effective_pct`
(= `discount_pct`, une ligne = une règle = un catalog, plus de notion de taux combiné —
voir correction en §2), `catalog_name` (catalog Shopify cible — voir
[liste des Catalogs](#liste-des-catalogs-à-créer-mise-à-jour-19-août-2026)).

Sert de base au futur `generate_companies.py` (une Company par club, un Catalog/Price list
par palier de remise et par boutique). Contient des noms de clients réels — gitignoré comme
les autres exports bruts, pas dans les fichiers `_sample_*.csv` versionnés.

---

## 4. Ouvert — à valider avec le client

### Blocages pour `generate_companies.py`

| Sujet | Statut |
|---|---|
| **Butterfly dépasse la limite de 3 catalogs (Basic)** | 4 catalogs nécessaires pour une fidélité complète (voir [liste](#liste-des-catalogs-à-créer-mise-à-jour-19-août-2026)) — décision à prendre : fusionner 2 catalogs (perte de fidélité sur 5 clubs) ou upgrade de plan |
| **Génération du contenu produit par Catalog** (`Included / <Catalog>`) | Pas encore scripté — nouveau step à construire depuis `export_magento_products_all.csv` (colonne `categories`) + exclusions SKU, indépendant de `generate_companies.py` (voir ci-dessus) |
| **Table `taux → nom de Catalog`** | ✅ Résolu côté Dandoy (19 août 2026) — les 2 Catalogs `Dandoy — Club 20%` / `Dandoy — Club 15%` créés manuellement avec les noms suggérés. Toujours en attente côté Butterfly (bloqué par la limite 3 catalogs, voir ci-dessus) |
| **Colonne Matrixify `Location: Catalogs`** | ✅ Confirmé (19 août 2026) — colonne existe bien, valeur = nom du catalog (ex. `Dandoy — Club 20%`, `Dandoy — Club 15%`). Absente du fichier demo statique inspecté, mais présente dans l'app réelle |
| **Adresse par club** (`Location: Shipping/Billing Address`, `City`, `Zip`, `Country Code`) | ✅ Résolu (19 août 2026) — décision du client : import sans adresse, complément manuel après migration |
| **`Main Contact: Customer Email`** (contact principal par club) | ✅ Résolu (19 août 2026) — décision du client : import sans contact principal, complément manuel après migration |
| **Valeurs exactes de `Customer: Location Role`** | ✅ Confirmé (19 août 2026) — deux valeurs autorisées selon la doc Matrixify : `"Ordering only"` et `"Location admin"` |

### Pistes issues de la réflexion client (hors périmètre migration actuel)

| Sujet | Statut |
|---|---|
| **Dotation annuelle** (budget club calculé automatiquement sur cumul achats club + membres) | Process métier non retrouvé dans les données Magento actuelles — à faire préciser par le client (outil externe ? calcul manuel aujourd'hui ?) |
| **Auto-rattachement membre → club** à la création de compte | Aujourd'hui géré via fichier Excel côté client — à voir si B2B Companies (invitation par le club) remplace ce process, ou si l'import initial suffit |
| **Portail clubs complet** (tableau de bord, historique, statistiques par saison, sponsoring, réservation démos) | Hors périmètre migration — développement complémentaire éventuel, post-migration |
| **Personnalisation textile par joueur** (taille/prénom/numéro/sponsor) | Existe déjà côté Custom Options (line item properties) — voir [Custom Options](./custom-options.md) — pas besoin de B2B pour ça |
| **Produits exclusifs clubs/revendeurs** | Faisable via Catalogs B2B, sur les deux boutiques — la limite de 3 catalogues actifs côté Butterfly (Basic) est déjà consommée par les remises club (4 nécessaires, voir ci-dessus), donc aucune marge pour un catalog supplémentaire sans upgrade |

---

## Sources

- `01_DATA_RAW/customer_group.csv`, `01_DATA_RAW/cart_price_rules.csv`, `01_DATA_RAW/export_customer.csv`
- `02_ANALYSIS_AND_MAPPING/DOC/Réflexion club-membres-remises.docx` (recherche client)
