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

| Règle Magento | Taux | Portée | # clubs |
|---|---|---|---|
| `Remises club 20% - Dandoy` | 20 % | Dandoy | 41 |
| `Remises club 15% - Dandoy` | 15 % | Dandoy | 44 |
| `Remises club 15% - Butterfly` | 15 % | Butterfly | 49 (dont 5 cumulent aussi 5 % + 7 %, voir ci-dessous) |
| `Remises club 10% - Butterfly` | 10 % | Butterfly | 27 |
| `Remises club 7% - Butterfly` | 7 % | Butterfly | 5 (groupes 20/88/89/93/95 — `website_id=4`/BE uniquement, pas NL) |
| `Remises club 5% - Butterfly` | 5 % | Butterfly | 5 (mêmes 5 clubs que ci-dessus) |
| `Remise club 5% addition STIGA` | 6,25 % | Produits STIGA uniquement | 2 (groupes 29, 62) |
| `Sofiane Boukoula` | 30 % | Nominatif | 1 client |

**Points clés :**
- Le taux **diffère selon la marque** pour un même club (17 clubs ont un taux Dandoy ET
  un taux Butterfly différents) — cohérent avec Option B (deux boutiques séparées).
- Ces remises club **s'additionnent** aux paliers panier génériques (`5% apd 50€`, etc.,
  eux aussi permanents et automatiques) — ce qui explique le taux de remise moyen assez
  homogène (~20-27 %) observé en analysant `export_order_all_2025_2026.csv` par groupe.
- **Les règles club elles-mêmes s'empilent entre elles** : toutes ont
  `stop_rules_processing=0`, donc pour les 5 clubs Butterfly avec 15 %+5 %+7 %, le taux
  effectif combiné est **~24,9 %** (calcul multiplicatif séquentiel : `1-(0,85×0,95×0,93)`,
  à confirmer sur une commande réelle avant de figer le taux du catalog Shopify — Magento
  applique peut-être un cumul additif selon sa config exacte).
- Aucune donnée de **tier price par produit** (`catalog_product_entity_tier_price`) n'a
  été trouvée dans l'export produits — les remises sont uniquement au niveau panier/%,
  pas de grille tarifaire produit par produit à ce stade.
- Deux cas hors norme, à traiter à part (pas de catalog dédié standard) : **STIGA addition**
  (groupes 29, 62 — +6,25 % uniquement sur les produits STIGA, en plus du 20 % Dandoy) et
  **Sofiane Boukoula** (groupe 10 — 30 % nominatif, Dandoy uniquement ; ce même client a un
  taux standard 15 % côté Butterfly).

### Référence — rule_id des 8 règles club

| rule_id | Nom | Catalog Shopify cible |
|---|---|---|
| `3983` | Remises club 15% - Dandoy | `Dandoy — Club 15%` |
| `4048` | Remises club 20% - Dandoy | `Dandoy — Club 20%` |
| `4049` | Remises club 15% - Butterfly | `Butterfly — Club 15%` |
| `4226` | Remises club 10% - Butterfly | `Butterfly — Club 10%` |
| `7969` | Remises club 5% - Butterfly | `Butterfly — Club Premium` (cumulée) |
| `7970` | Remises club 7% - Butterfly | `Butterfly — Club Premium` (cumulée) |
| `5331` | Remise club 5% addition STIGA | cas particulier (hors catalog standard) |
| `5695` | Sofiane Boukoula | cas particulier (hors catalog standard) |

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
- Seule limite réelle à surveiller côté Butterfly : **3 catalogues actifs max**. En
  recomptant les taux réels (15 %, 10 %, et le palier cumulé ~24,9 % pour 5 clubs), ça
  tient exactement en 3 catalogues — mais toute règle supplémentaire à l'avenir dépassera
  cette limite.

### Liste des Catalogs à créer (14 août 2026)

| Boutique | Catalog | Remise | # clubs |
|---|---|---|---|
| Dandoy-Sports | `Dandoy — Club 20%` | 20 % | 41 |
| Dandoy-Sports | `Dandoy — Club 15%` | 15 % | 44 |
| Butterfly TT | `Butterfly — Club 15%` | 15 % | 44 |
| Butterfly TT | `Butterfly — Club 10%` | 10 % | 27 |
| Butterfly TT | `Butterfly — Club Premium` | ~24,9 % (15 %+5 %+7 % cumulés, à confirmer) | 5 |

**5 catalogs standards** (2 Dandoy + 3 Butterfly). Les deux cas particuliers (STIGA
addition, compte nominatif Boukoula) restent **hors de cette liste** — à trancher avec le
client avant de décider s'ils méritent un catalog dédié ou un traitement manuel.

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

#### Catalogs — création manuelle obligatoire

**Matrixify ne peut pas créer de Catalog** (nom, produits, % de remise) — confirmé par le
tutoriel Matrixify sur le pricing produit par marché/catalog : la création se fait
uniquement dans Shopify Admin (Settings → B2B / Markets). Une fois le Catalog créé à la
main avec sa remise en %, Matrixify peut y rattacher des produits et fixer des prix fixes
par variante (`Included / <Catalog>`, `Price / <Catalog>` sur le sheet Products), mais pas
poser une règle en pourcentage.

**Décision (14 août 2026) :** le client crée manuellement les Catalogs (un par palier de
remise × par boutique — 2 pour Dandoy, 3 pour Butterfly, voir §1) et fournit la table
`taux → nom du Catalog Shopify`. Le rattachement Company → Catalog se fait ensuite via la
colonne `Location: Catalogs` (nom de colonne indiqué par le client) — **à confirmer** : cette
colonne n'apparaît pas dans le fichier demo Companies inspecté (43 colonnes listées
ci-dessus, aucune catalogue) ; il faudra vérifier son existence/format exact directement
dans l'app Matrixify (peut-être ajoutée depuis, ou disponible sur un sheet distinct) avant
d'écrire `generate_companies.py`.

Un nouveau script `generate_companies.py` est à prévoir (généré depuis
`club_discount_mapping.csv` + la table de correspondance Catalogs fournie par le client), à
ajouter à `regenerate_all.sh` et à l'ordre d'import Matrixify de `CLAUDE.md` (après
`shopify_customers_*.csv`, avant les traductions/redirections).

---

## 3. Mapping des 88 clubs (group_id → nom → taux)

Généré dans `02_ANALYSIS_AND_MAPPING/club_discount_mapping.csv` (174 lignes — une ligne par
club × règle Magento, donc plusieurs lignes par club quand plusieurs règles s'empilent, ex.
les 5 clubs Butterfly Premium) depuis `cart_price_rules.csv` + `customer_group.csv`.
Colonnes : `group_id`, `club_name`, `brand`, `discount_pct` (taux de la règle individuelle),
`magento_rule`, `rule_id`, `nb_clients`, `catalog_effective_pct` (taux combiné une fois
toutes les règles du groupe empilées), `catalog_name` (catalog Shopify cible — voir
[liste des Catalogs](#liste-des-catalogs-à-créer-14-août-2026)).

Sert de base au futur `generate_companies.py` (une Company par club, un Catalog/Price list
par palier de remise et par boutique). Contient des noms de clients réels — gitignoré comme
les autres exports bruts, pas dans les fichiers `_sample_*.csv` versionnés.

---

## 4. Ouvert — à valider avec le client

### Blocages pour `generate_companies.py`

| Sujet | Statut |
|---|---|
| **Table `taux → nom de Catalog`** | En cours — client crée les Catalogs manuellement dans Shopify Admin et fournira les noms |
| **Colonne Matrixify `Location: Catalogs`** | À confirmer directement dans l'app (absente du fichier demo Companies inspecté) |
| **Adresse par club** (`Location: Shipping/Billing Address`, `City`, `Zip`, `Country Code`) | Aucune donnée d'adresse club dans les exports Magento (seulement des adresses individuelles de membres) — à demander au client, ou import avec pays seul en attendant complément manuel |
| **`Main Contact: Customer Email`** (contact principal par club) | Aucun signal exploitable dans les données — proposition : le client avec le plus d'historique de commandes dans le groupe, à valider |
| **Valeurs exactes de `Customer: Location Role`** | Probablement `"Ordering only"` / `"Location admin"` (terminologie Shopify), non confirmées dans le fichier demo (colonne vide) — à vérifier avant génération |

### Pistes issues de la réflexion client (hors périmètre migration actuel)

| Sujet | Statut |
|---|---|
| **Dotation annuelle** (budget club calculé automatiquement sur cumul achats club + membres) | Process métier non retrouvé dans les données Magento actuelles — à faire préciser par le client (outil externe ? calcul manuel aujourd'hui ?) |
| **Auto-rattachement membre → club** à la création de compte | Aujourd'hui géré via fichier Excel côté client — à voir si B2B Companies (invitation par le club) remplace ce process, ou si l'import initial suffit |
| **Portail clubs complet** (tableau de bord, historique, statistiques par saison, sponsoring, réservation démos) | Hors périmètre migration — développement complémentaire éventuel, post-migration |
| **Personnalisation textile par joueur** (taille/prénom/numéro/sponsor) | Existe déjà côté Custom Options (line item properties) — voir [Custom Options](./custom-options.md) — pas besoin de B2B pour ça |
| **Produits exclusifs clubs/revendeurs** | Faisable via Catalogs B2B, sur les deux boutiques — attention à la limite de 3 catalogues actifs côté Butterfly (Basic) |

---

## Sources

- `01_DATA_RAW/customer_group.csv`, `01_DATA_RAW/cart_price_rules.csv`, `01_DATA_RAW/export_customer.csv`
- `02_ANALYSIS_AND_MAPPING/DOC/Réflexion club-membres-remises.docx` (recherche client)
