# Migration des chèques cadeaux (gift cards)

> **Statut : à faire** — analyse effectuée le 5 août 2026, aucun script de conversion écrit,
> décision de méthode en attente.

---

## Différence avec les codes promo

À ne pas confondre avec les règles de panier Magento (`salesrule`/codes promo en %, montant
fixe, etc.) : aucun export n'existe pour ces règles à ce stade, sujet non commencé.

Les **chèques cadeaux** sont un mécanisme différent : une valeur stockée avec un solde qui se
décrémente à l'usage, offerte par un client à un destinataire (nom, email, message inclus dans
l'export). Équivalent Shopify natif : **Gift Cards**.

---

## Données source

`01_DATA_RAW/gift_cards_export_file.csv` — 1 904 lignes brutes (dont doublons/en-têtes),
841 cartes valides après nettoyage.

| Colonne | Contenu |
|---|---|
| `Card ID`, `Card Code` | Identifiant + code carte (format confirmé : 17 caractères, `XXXXX-XXXXX-XXXXX`) |
| `Card Amount`, `Card Balance`, `Card Currency` | Montant initial, solde restant, devise (100% EUR) |
| `Card Type`, `Card Status` | Type (quasi 100% = `1`) ; **statut confirmé par le client : `1` = active, `2` = utilisée (used)** |
| `Mail From`, `Mail To`, `User Email`, `Message` | Expéditeur, destinataire, email, message cadeau |
| `Country`/`State`/`City`/`Street`/`Zip`/`Phone` | Quasi entièrement vides dans ce jeu de données |
| `Customer ID`, `Created Date`, `Expiration Date` | `Expiration Date` quasi jamais renseignée (1 seule ligne sur 841) |
| `Store Code`, `Group Name` | Portée boutique(s) — voir routage ci-dessous |

### Répartition par statut

| `Card Status` | Nb cartes | Solde total |
|---|---|---|
| `1` (active) | 281 | **9 247,49 €** |
| `2` (utilisée) | 559 | 10 010,98 € (non concerné — solde déjà consommé) |

→ **Seules les 281 cartes actives (solde total 9 247,49 €) doivent être migrées.** Les cartes
utilisées n'ont pas besoin d'exister côté Shopify.

### Routage boutique (`Store Code`)

Comme pour les commandes, chaque carte doit être routée vers la boutique Shopify d'origine.
`Store Code` référence les vues Magento (`eu_fr`, `eu_en`, `eu_nl`, `ww_en` → Dandoy-Sports ;
`bt_be_fr`, `bt_nl`, `bt_be_en`, `bt_be_nl` → Butterfly TT), mais **contrairement aux
commandes**, une carte peut lister plusieurs stores séparés par une virgule (portée d'usage
multi-sites), y compris à cheval sur les deux marques :

| `Store Code` (cartes actives) | Nb |
|---|---|
| `eu_fr` | 161 |
| `ww_en` | 41 |
| `eu_fr,eu_en,eu_nl` | 38 |
| `eu_nl` | 25 |
| `eu_en` | 5 |
| `ALL` | 3 |
| `eu_fr,bt_be_fr` | 2 |
| `bt_nl` | 2 |
| autres combinaisons | 1 chacune |

→ Décision à prendre : dupliquer les cartes à portée mixte Dandoy/Butterfly dans les deux
fichiers de sortie (comme les 199 produits partagés), ou les router vers une seule boutique
par défaut (ex. Dandoy, marque principale). Impact estimé faible (≤5 cartes concernées).

---

## Deux méthodes de migration possibles

### Option A — Matrixify (import Orders avec ligne Gift Card)

Technique documentée officiellement par Matrixify : importer une commande avec une ligne
Gift Card, ce qui déclenche l'émission automatique d'une carte cadeau Shopify.

- ✅ Pas de script à écrire — CSV au format Orders, pipeline déjà maîtrisé
  (voir [Historique des commandes](./orders.md))
- ⚠️ **Limitation confirmée par la doc officielle : les codes existants ne sont PAS
  préservés** — Shopify génère un nouveau code à chaque carte. Impliquerait de recontacter
  les 281 titulaires pour leur communiquer leur nouveau code.
- ⚠️ Dates d'expiration non migrées (non bloquant ici — quasi aucune carte n'en a).

Source : [Migrate Gift Cards between Shopify stores using Gift Card Orders — Matrixify](https://matrixify.app/tutorials/migrate-gift-cards-between-shopify-stores-using-gift-card-orders/)

### Option B — API Admin GraphQL (`giftCardCreate`)

- ✅ Permet de **fixer le code existant** (`code` en paramètre de la mutation) — aucune
  communication client nécessaire, transparent pour les 281 titulaires
- ✅ Ne nécessite pas de plan Shopify Plus — fonctionne via une app privée/custom avec le
  scope `write_gift_cards` (confirmé par la communauté Shopify, cf. sources)
- ⚠️ Nécessite un script Python dédié (appels API), pas de réutilisation de Matrixify

Sources : [giftCardCreate mutation — Shopify.dev](https://shopify.dev/docs/api/admin-graphql/latest/mutations/giftCardCreate),
[Shopify Api Create Gift Cards — communauté Shopify](https://community.shopify.com/t/shopify-api-create-gift-cards/157529)

### Recommandation

Étant donné qu'il s'agit d'argent réel déjà détenu par des clients (9 247,49 € sur 281
cartes), **l'Option B (API, code préservé)** limite le risque support/communication client par
rapport à l'Option A. Décision finale à valider avec le client.

---

## Reste à faire

- [ ] Décider Option A (Matrixify, nouveaux codes) vs Option B (API, codes préservés)
- [ ] Décider du routage des cartes à portée mixte Dandoy/Butterfly (≤5 cartes)
- [ ] Écrire le script de conversion/migration (`magento_to_shopify_giftcards.py` ou script API dédié)
- [ ] Tester sur un échantillon avant migration complète des 281 cartes actives
