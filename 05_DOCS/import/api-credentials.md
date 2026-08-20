# Identifiants API Admin (app privée de migration)

> **Statut : à faire** — app créée et installée sur Dandoy-Sports (5 août 2026), mais
> l'obtention du token a nécessité un changement de méthode en cours de route (voir
> ci-dessous). Token définitif pas encore généré. Butterfly TT pas encore fait.

---

## Pourquoi une app privée (et pas la Shopify CLI)

Deux chantiers de ce projet n'ont **aucun chemin d'import CSV/Matrixify** et doivent passer par
l'API Admin directement :

| Chantier | Pourquoi pas de CSV | Mutation API |
|---|---|---|
| [Chèques cadeaux](./gift-cards.md) (Option B — codes préservés) | L'API Gift Card n'est pas exposée via un template Matrixify | `giftCardCreate` |
| Codes promo / cart price rules (`salesrule` Magento) | Shopify Discounts n'a pas de bulk import CSV natif | `discountCodeBasicCreate`, `discountAutomaticBasicCreate` (à confirmer selon les types de règles trouvés) |

Plutôt qu'une app par chantier, **une seule app d'outillage par boutique** couvre les deux
besoins (et tout autre script API ponctuel qui apparaîtrait d'ici le go-live) — un seul jeu
d'identifiants à gérer/stocker/révoquer.

---

## Nom de l'app

**`Migration Tooling — Magento2Shopify`**, créée à l'identique dans les deux boutiques
(Dandoy-Sports et Butterfly TT).

---

## ⚠️ Changement de modèle Shopify (2026) — ce qui a coincé

Depuis le 1er janvier 2026, Shopify a retiré la création d'apps privées "à l'ancienne"
(Settings → Develop apps → Install → token `shpat_` révélé une fois). Toute nouvelle app passe
désormais par le **Dev Dashboard**, ce qui a introduit plusieurs pièges rencontrés en marche :

1. **Le Dev Dashboard a deux notions de "token" distinctes** — le premier trouvé
   (`Jeton d'automatisation d'application`, préfixe `atkn_`) sert uniquement à authentifier la
   **Shopify CLI** pour du CI/CD (`shopify app deploy`), pas à appeler l'API Admin. Ce n'est pas
   ce qu'il faut ici.
2. **Le Client Credentials Grant (`client_id` + `client_secret` → token en un appel HTTP) ne
   fonctionne QUE sur les boutiques de développement.** Testé le 5 août 2026 sur `dandoy-sports`
   (boutique payante) → échec systématique `Oauth error shop_not_permitted: Client credentials
   cannot be performed on this shop`, quelle que soit l'installation ou l'organisation. C'est une
   restriction volontaire de Shopify, pas un problème de configuration.
3. **Seul flow qui fonctionne sur une boutique payante : l'Authorization Code Grant** — un flow
   OAuth interactif (une seule fois), qui donne ensuite un **token permanent**, offline, au
   comportement identique à l'ancien `shpat_` statique.

---

## Scopes requis

| Scope | Pour |
|---|---|
| `write_gift_cards` (+ `read_gift_cards`) | Migration des 281 chèques cadeaux actifs |
| `write_discounts` (+ `read_discounts`) | Migration des codes promo — à activer quand l'export `salesrule` sera fourni |

Scope additionnel possible plus tard : `read_customers`, si on veut un jour lier le
destinataire d'une gift card à son compte client Shopify existant (`recipientAttributes` de
`giftCardCreate`) — non activé pour l'instant.

---

## Procédure (à répéter dans chaque boutique)

### 1. Créer et installer l'app (Dev Dashboard)

1. Admin Shopify → **Settings → Apps and sales channels → Develop apps** → **Build apps using
   Dev Dashboard**
2. **Create app** → nom `Migration Tooling — Magento2Shopify`
3. Configurer les **Admin API scopes** (voir ci-dessus)
4. Dans la config de l'app, **ajouter `http://localhost:8787/callback` aux redirect URLs
   autorisées** (nécessaire à l'étape 3 ci-dessous)
5. Installer l'app sur la boutique cible (le lien d'installation redirige vers l'Admin de la
   boutique pour confirmation)
6. Noter le **Client ID** (pas sensible) et le **Client secret** (`shpss_...`, sensible — à
   traiter comme un mot de passe, jamais collé dans un chat/log)

### 2. Préparer le fichier d'environnement local

Fichier **hors du repo git** (`.gitignore` couvre déjà `.dandoy_shopify_env` et `*.env`) :

```bash
export SHOPIFY_DANDOY_STORE_DOMAIN=dandoy-sports.myshopify.com
```

Le `Client secret` ne va **pas** dans ce fichier — il ne sert qu'une fois, à l'étape suivante,
via une variable d'environnement de session (`SHOPIFY_OAUTH_CLIENT_SECRET`), jamais écrite sur
disque.

### 3. Obtenir le token permanent (Authorization Code Grant)

```bash
export SHOPIFY_OAUTH_CLIENT_SECRET=shpss_xxxxx   # dans le shell, pas dans un fichier
python3 02_ANALYSIS_AND_MAPPING/SCRIPTS/get_shopify_access_token.py \
    --shop dandoy-sports.myshopify.com \
    --client-id 025239ab4713830c3756345fa1b7e914 \
    --scopes write_gift_cards,read_gift_cards \
    --env-file .dandoy_shopify_env \
    --token-var SHOPIFY_DANDOY_ACCESS_TOKEN
```

- Ouvre un navigateur pour approuver l'app sur la boutique (flow OAuth standard, une fois)
- Un **serveur local temporaire** (`localhost:8787`) capte le callback, vérifie le HMAC et le
  `state` (protection CSRF), puis échange le code contre le token
- Le token est **écrit directement dans le fichier d'env** — jamais affiché à l'écran, jamais
  dans un historique de conversation

---

## Variables d'environnement attendues par les scripts

```bash
export SHOPIFY_DANDOY_STORE_DOMAIN=dandoy-sports.myshopify.com
export SHOPIFY_DANDOY_ACCESS_TOKEN=...            # écrit par get_shopify_access_token.py
export SHOPIFY_BUTTERFLY_STORE_DOMAIN=butterfly-tt.myshopify.com
export SHOPIFY_BUTTERFLY_ACCESS_TOKEN=...
```

Utilisées par :
- `02_ANALYSIS_AND_MAPPING/SCRIPTS/migrate_giftcards_shopify.py` (`--execute`)
- futur script de migration des codes promo (à écrire quand l'export `salesrule` sera fourni)

---

## Règle de sécurité (rappel)

Aucun secret (Client secret, access token) ne doit jamais être collé directement dans une
conversation, un commit, ou un fichier suivi par git. Le `Client secret` initial a été partagé
en clair par erreur le 5 août 2026 — il a dû être considéré comme compromis et une bonne
pratique est de le régénérer ("Rotate secret") avant tout usage réel.

---

## À faire après le go-live

**Désinstaller l'app dans les deux boutiques** une fois tous les scripts API terminés — son
token reste valide et actif tant qu'elle n'est pas désinstallée.

---

## Reste à faire

- [x] Créer l'app dans la boutique Dandoy-Sports (Dev Dashboard, via l'org Partner Quai31) —
      confirmé installée par capture d'écran (`SCREENSHOTS_MIGRATION_TOOLING/app_custom_migration_tooling.png`),
      scopes Cartes-cadeaux + Réductions + Clients tous accordés (Consultation + Modification)
- [x] Comprendre pourquoi Client Credentials Grant échoue sur boutique payante (`shop_not_permitted`)
- [x] Écrire `get_shopify_access_token.py` (Authorization Code Grant, serveur local, token jamais affiché)
- [ ] Enregistrer `http://localhost:8787/callback` dans les redirect URLs de l'app Dandoy
- [ ] Lancer `get_shopify_access_token.py` pour Dandoy-Sports et obtenir le token permanent
- [ ] Créer l'app + obtenir le token pour Butterfly TT
- [ ] Lancer `migrate_giftcards_shopify.py --shop dandoy --execute --limit 5` en test
- [ ] Désinstaller les deux apps après le go-live
