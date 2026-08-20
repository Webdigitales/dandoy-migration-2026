# Migration des chèques cadeaux (gift cards)

> **Statut : à faire** — **Option B retenue** (API, code préservé). Script écrit et testé en
> dry-run le 5 août 2026 — migration réelle (`--execute`) pas encore lancée, en attente des
> identifiants API des deux boutiques.

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

### Décision : Option B retenue

Étant donné qu'il s'agit d'argent réel déjà détenu par des clients (9 247,49 € sur 281
cartes), **l'Option B (API, code préservé)** limite le risque support/communication client par
rapport à l'Option A. Retenue le 5 août 2026.

---

## Script de migration

```bash
# Dry-run (par défaut, rien n'est envoyé à Shopify) :
python3 02_ANALYSIS_AND_MAPPING/SCRIPTS/migrate_giftcards_shopify.py --shop dandoy
python3 02_ANALYSIS_AND_MAPPING/SCRIPTS/migrate_giftcards_shopify.py --shop butterfly

# Migration réelle (nécessite les identifiants API en variables d'environnement) :
python3 02_ANALYSIS_AND_MAPPING/SCRIPTS/migrate_giftcards_shopify.py --shop dandoy --execute
```

- Appelle la mutation Admin GraphQL `giftCardCreate` directement (pas de CSV Matrixify — l'API
  Gift Card n'est pas accessible via un template Matrixify).
- **Non intégré à `regenerate_all.sh`** : contrairement aux autres scripts du pipeline, celui-ci
  a un effet de bord réel et irréversible (création de valeur stockée réelle côté Shopify) —
  volontairement tenu à l'écart de la régénération automatique.
- Dry-run par défaut ; `--execute` requiert les variables d'environnement
  `SHOPIFY_{DANDOY|BUTTERFLY}_STORE_DOMAIN` et `SHOPIFY_{DANDOY|BUTTERFLY}_ACCESS_TOKEN` — voir
  [Identifiants API](./api-credentials.md) pour la création de l'app privée et ses scopes.
- `--limit N` pour tester sur un petit échantillon avant la migration complète.
- Un rapport CSV est écrit par boutique
  (`04_SHOPIFY_IMPORTS/giftcards_migration_report_{dandoy|butterfly}.csv`, gitignoré) avec le
  statut de chaque carte (`DRY-RUN` / `CREATED` / `ERROR`).
- Testé en dry-run le 5 août 2026 : **276 cartes routées vers Dandoy, 10 vers Butterfly**
  (271 Dandoy-only + 5 Butterfly-only + 5 cartes à portée mixte dupliquées dans les deux —
  cohérent avec le tableau de répartition ci-dessus).
- **Liaison automatique au compte client** : pour chaque carte, le script recherche un client
  Shopify existant par email (`User Email` Magento) et attache `customerId` à la mutation si
  trouvé, sinon la carte reste non liée (cas guest, ou client pas encore importé). Rapport
  colonnes `recipient_email` / `matched_customer_id` pour audit.
- **Test réel confirmé le 20 août 2026** (1 carte, `1QRKR-SJQ17-8Z7WP`, 50 €) : créée avec
  succès côté API (`giftCardCreate` → `enabled: true`), invisible dans l'Admin au premier coup
  d'œil car l'Admin masque/tronque le code affiché — confirmé exister via une requête
  `giftCard(id: ...)` directe. **Non liée à un client** car la boutique de test ne contient que
  563 clients importés (échantillon), pas les 33 357 clients Dandoy attendus.
- ⚠️ **Ordre de migration important** : lancer la migration des gift cards **après** l'import
  complet des clients (`shopify_customers_dandoy.csv`), sinon la quasi-totalité des cartes
  resteront non liées à un compte alors qu'un lien existe potentiellement côté Magento.

---

## Reste à faire

- [x] Décider Option A (Matrixify, nouveaux codes) vs Option B (API, codes préservés) — **Option B retenue**
- [x] Écrire le script de migration (`migrate_giftcards_shopify.py`)
- [x] Valider le routage en dry-run (276 Dandoy / 10 Butterfly, cohérent avec l'analyse)
- [x] Obtenir les identifiants API côté Dandoy (Authorization Code Grant — voir [Identifiants API](./api-credentials.md))
- [x] Tester `--execute --limit 1` en réel — confirmé fonctionnel (carte créée, code + solde corrects)
- [x] Ajouter la liaison automatique au compte client (`customerId` par email)
- [ ] Importer les 33 357 clients Dandoy dans Shopify (prérequis pour que la liaison client fonctionne à l'échelle)
- [ ] Obtenir les identifiants API côté Butterfly
- [ ] Lancer la migration complète des 276 cartes Dandoy + 10 Butterfly (après import clients)
- [ ] Vérifier dans l'Admin Shopify (Products → Gift Cards) que codes, soldes et liaisons client correspondent
