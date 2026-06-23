# Gestion multi-sites Magento → Shopify — Dandoy-Sports / Butterfly TT

---

## Situation actuelle sur Magento

### Websites Magento

| Code website | Domaine(s) | Store views |
|---|---|---|
| `base` | dandoy-sports.com (principal) | `eu_fr`, `eu_nl`, `eu_en` |
| `ds_ww` | dandoy-sports.com (international) | `ww_en` |
| `bt_be` | be.butterfly.tt (Butterfly Belgique) | `bt_be_fr`, `bt_be_nl` |
| `bt_nl` | nl.butterfly.tt (Butterfly Pays-Bas) | `bt_nl` |

### Store views obsolètes (à ne pas migrer)

| Store view | Raison |
|---|---|
| `eu_en_old` | Ancienne vue anglaise Dandoy, remplacée par `eu_en`. Contient 3 413 lignes dans l'export mais n'est plus utilisée en production. |
| `bt_be_en` | Vue anglaise Butterfly Belgique, non utilisée. Contient 1 103 lignes dans l'export. |

> **Important :** ces store views doivent être **exclues** lors de l'extraction des traductions
> pour Shopify. Seules les store views listées dans le tableau ci-dessus sont à migrer.

### Distribution des produits par domaine

| Domaine | Total | Actifs | Désactivés |
|---|---|---|---|
| `dandoy-sports.com` | 4 258 | 2 033 | 2 225 |
| `fr.dandoy-sports.eu` | 4 248 | 2 029 | 2 219 |
| `en.dandoy-sports.eu` | 4 248 | 2 029 | 2 219 |
| `nl.dandoy-sports.eu` | 4 248 | 2 029 | 2 219 |
| `be.butterfly.tt` | 880 | 350 | 530 |
| `nl.butterfly.tt` | 881 | 351 | 530 |

> Les 3 sous-domaines Dandoy EU (fr/en/nl) partagent le même catalogue — seule la langue change.

### Produits partagés entre Dandoy et Butterfly

| | Total | Actifs |
|---|---|---|
| Dandoy uniquement | 4 059 | 1 998 |
| Butterfly uniquement | 683 | 316 |
| **Partagés** (sur les deux) | **199** | **35** |
| **Total produits uniques** | **4 941** | **2 349** |

### Périmètre cible Shopify (6 domaines)

1. `dandoy-sports.com` (principal)
2. `fr.dandoy-sports.eu` (FR)
3. `en.dandoy-sports.eu` (EN)
4. `nl.dandoy-sports.eu` (NL)
5. `be.butterfly.tt` (Butterfly BE)
6. `nl.butterfly.tt` (Butterfly NL)

---

## Option A — Instance unique + Shopify Markets (recommandée)

### Principe

Tous les produits (27 939) dans **un seul catalogue** Shopify. La séparation Dandoy / Butterfly
est gérée par **Shopify Markets** + **collections automatiques** basées sur des tags.

### Mise en oeuvre

#### 1. Tags de scope

Ajouter un tag `brand:xxx` dans le CSV d'import selon `product_websites` :

| `product_websites` Magento | Tags ajoutés |
|---|---|
| `base`, `base,ds_ww`, `ds_ww` | `brand:dandoy` |
| `bt_be`, `bt_nl`, `bt_be,bt_nl` | `brand:butterfly` |
| `base,ds_ww,bt_be,bt_nl` (et combinaisons mixtes) | `brand:dandoy`, `brand:butterfly` |

#### 2. Shopify Markets

| Marché | Domaines | Langues | Catalogue |
|---|---|---|---|
| **Dandoy EU** | `dandoy-sports.com`, `fr.dandoy-sports.eu`, `en.dandoy-sports.eu`, `nl.dandoy-sports.eu` | FR, EN, NL | Produits avec tag `brand:dandoy` |
| **Butterfly** | `be.butterfly.tt`, `nl.butterfly.tt` | FR, EN, NL | Produits avec tag `brand:butterfly` |

#### 3. Collections automatiques

- Collection "Catalogue Dandoy" → condition : tag = `brand:dandoy`
- Collection "Catalogue Butterfly" → condition : tag = `brand:butterfly`
- Utiliser la fonctionnalité **Market-specific catalog** (Shopify Markets) ou **Shopify Catalogs** (Plus)
  pour filtrer les produits visibles par marché.

#### 4. Traductions

Shopify Markets gère les traductions via l'API de traduction ou l'app **Translate & Adapt**.
Les contenus traduits (store views `eu_fr`, `eu_nl`, `bt_be_fr`, `bt_be_nl`…) peuvent être
importés via Matrixify dans les colonnes de traduction.

#### 5. Stock

Un seul flux Stock Sync → **un seul inventaire** pour tous les marchés. Pas de risque de survente.

### Avantages

- **Stock unifié** : une seule source de vérité, pas de risque de survente
- **Un seul abonnement** Shopify
- **Gestion centralisée** : prix, descriptions, images au même endroit
- **Produits partagés** (199, dont 35 actifs) : aucune duplication, visibles sur les deux marques

### Inconvénients

- Configuration Markets plus complexe au départ
- Les thèmes Dandoy et Butterfly partagent la même boutique (nécessite un thème adaptatif
  ou des sections conditionnelles par marché)
- Nécessite Shopify Plus pour les **Catalogs** (filtrage catalogue par marché),
  ou une app tierce sur un plan inférieur

---

## Option B — Deux boutiques Shopify séparées

### Principe

Deux instances Shopify indépendantes, chacune avec son propre catalogue.

| Boutique | Domaines | Produits |
|---|---|---|
| **Dandoy-Sports** | `dandoy-sports.com`, `fr/en/nl.dandoy-sports.eu` | ~24 023 (base + ds_ww + partagés) |
| **Butterfly TT** | `be.butterfly.tt`, `nl.butterfly.tt` | ~5 277 (bt_be + bt_nl + partagés) |

Les **199 produits partagés (dont 35 actifs)** sont dupliqués dans les deux boutiques.

### Mise en oeuvre

#### 1. Fichiers d'import

Le script de conversion génère deux fichiers :

- `shopify_products_dandoy.csv` — produits dont `product_websites` contient `base` ou `ds_ww`
- `shopify_products_butterfly.csv` — produits dont `product_websites` contient `bt_be` ou `bt_nl`

#### 2. Traductions

Chaque boutique gère ses langues via Shopify Markets :

| Boutique | Store views sources | Langues |
|---|---|---|
| **Dandoy** | `eu_fr`, `eu_en`, `eu_nl`, `ww_en` | FR, EN, NL |
| **Butterfly** | `bt_be_fr`, `bt_be_nl`, `bt_nl` | FR, NL |

#### 3. Stock

Stock Sync configuré sur les deux boutiques, connecté au même serveur SFTP.
Le même fichier CSV de stock alimente les deux (les SKU sont identiques).

### Avantages

- Catalogue **propre par marque** : pas de logique de filtrage
- **Thème indépendant** par boutique : branding Butterfly strict respecté
- Gestion indépendante des prix, promotions, pages CMS

### Inconvénients

- **199 produits dupliqués** (dont 35 actifs) → double maintenance (prix, descriptions, images)
- **Risque de survente** sur les produits partagés : la sync stock est 1×/jour,
  si le dernier stock est vendu sur Dandoy, Butterfly ne le sait pas avant le lendemain
- **Deux abonnements** Shopify (coût doublé)
- **Deux configs** Stock Sync, deux thèmes à maintenir
- Modification d'un produit partagé → à faire dans les deux boutiques

---

## Comparatif

| Critère | Option A (instance unique) | Option B (deux boutiques) |
|---|---|---|
| Stock | Unifié, pas de survente | Dupliqué, risque de survente (sync 1×/jour) |
| Produits partagés (199) | Gérés nativement | Dupliqués manuellement |
| Coût Shopify | 1 abonnement | 2 abonnements |
| Branding Butterfly | Thème adaptatif ou sections conditionnelles | Thème 100% dédié |
| Complexité initiale | Plus élevée (Markets, Catalogs) | Plus simple |
| Maintenance quotidienne | Centralisée | Double effort sur les partagés |
| Stock Sync | 1 connexion SFTP | 2 connexions SFTP |
| Traductions | Translate & Adapt (1 boutique) | Translate & Adapt (× 2) |

---

## Recommandation

**Option A (instance unique)** est recommandée pour ce projet car :

1. Le stock sans ERP et la sync 1×/jour rendent la **survente** très probable avec deux boutiques
2. Les **199 produits partagés (dont 35 actifs)** représentent un effort de maintenance significatif en double
3. Shopify Markets couvre le besoin multi-domaine / multi-langue nativement
4. Un seul flux Stock Sync simplifie l'infrastructure

L'Option B reste pertinente si le branding Butterfly exige une **séparation totale**
(thème, expérience, équipe de gestion distincte) et que le risque de survente sur les
produits partagés est accepté.
