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
| `Remises club 15% - Butterfly` | 15 % | Butterfly | 49 |
| `Remises club 10% - Butterfly` | 10 % | Butterfly | 27 |
| `Remises club 7% - Butterfly` | 7 % | Butterfly | 5 |
| `Remises club 5% - Butterfly` | 5 % | Butterfly | 5 (mêmes clubs, cumulé avec 7 %) |
| `Remise club 5% addition STIGA` | 6,25 % | Produits STIGA uniquement | 2 (groupes 29, 62) |
| `Sofiane Boukoula` | 30 % | Nominatif | 1 client |

**Points clés :**
- Le taux **diffère selon la marque** pour un même club (17 clubs ont un taux Dandoy ET
  un taux Butterfly différents) — cohérent avec Option B (deux boutiques séparées).
- Ces remises club **s'additionnent** aux paliers panier génériques (`5% apd 50€`, etc.,
  eux aussi permanents et automatiques) — ce qui explique le taux de remise moyen assez
  homogène (~20-27 %) observé en analysant `export_order_all_2025_2026.csv` par groupe.
- Aucune donnée de **tier price par produit** (`catalog_product_entity_tier_price`) n'a
  été trouvée dans l'export produits — les remises sont uniquement au niveau panier/%,
  pas de grille tarifaire produit par produit à ce stade.

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
  recomptant les taux réels (15 %, 10 %, et 5+7 % cumulé pour 5 clubs), ça tient exactement
  en 3 catalogues — mais toute règle supplémentaire à l'avenir dépassera cette limite.

### Import en masse via Matrixify

Matrixify supporte un sheet dédié **Companies** (`Bulk import Shopify B2B Companies`) :

- Colonnes : nom de company, locations (adresse/contact/téléphone/langue), contacts clients
  (email/ID + rôle), catalogues/price lists par location, conditions de paiement (Net 7-90),
  exonérations fiscales.
- Commandes `NEW` / `MERGE` / `UPDATE` / `REPLACE` / `DELETE` — réimportable comme le reste
  du pipeline.
- **Prérequis strict : les clients doivent déjà exister dans Shopify avant l'import
  Companies**, sinon échec (liaison par email ou ID). Implique l'ordre d'import :
  `shopify_customers_*.csv` → `shopify_companies_*.csv`.
- Aucune restriction de plan Matrixify spécifique aux Companies (Enterprise déjà prévu pour
  le premier mois — largement suffisant pour 88 companies).

Un nouveau script `generate_companies.py` est à prévoir (généré depuis
`club_discount_mapping.csv`), à ajouter à `regenerate_all.sh` et à l'ordre d'import Matrixify
de `CLAUDE.md` (après `shopify_customers_*.csv`, avant les traductions/redirections).

---

## 3. Mapping des 88 clubs (group_id → nom → taux)

Généré dans `02_ANALYSIS_AND_MAPPING/club_discount_mapping.csv` (174 lignes — une ligne par
club × marque quand le taux diffère entre Dandoy et Butterfly) depuis `cart_price_rules.csv` +
`customer_group.csv`. Colonnes : `group_id`, `club_name`, `brand`, `discount_pct`,
`magento_rule`, `rule_id`, `nb_clients`.

Sert de base au futur `generate_companies.py` (une Company par club, un Catalog/Price list
par palier de remise et par boutique). Contient des noms de clients réels — gitignoré comme
les autres exports bruts, pas dans les fichiers `_sample_*.csv` versionnés.

---

## 4. Ouvert — à valider avec le client

Ces points viennent de la réflexion transmise par le client et **ne sont pas dans le
périmètre actuel du projet** — à trancher avant tout développement :

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
