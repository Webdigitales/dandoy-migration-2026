# Redirections 301 — Migration Magento → Shopify

> **Deux boutiques Shopify (Option B)** : chaque boutique n'a besoin de rediriger que les
> produits/catégories effectivement présents dans son catalogue. `generate_redirects.py`
> scope automatiquement chaque redirection à la bonne boutique via `product_websites`
> (fonction `brand_scope()`, partagée avec `magento_to_shopify.py`) — voir
> [Multi-sites](../architecture/multi-sites.md).

---

## Vue d'ensemble

| Type de redirection | Dandoy-Sports | Butterfly TT |
|---|---|---|
| **Produits actifs** | 2 014 | 355 |
| **Catégories** | 31 | 25 |
| **Total** | **2 045** | **380** |

### Ce qui n'est PAS redirigé (vérifié par tests HTTP + scope boutique)

| Type | Raison |
|---|---|
| Produits désactivés (`product_online=2`) | Déjà en 404 sur Magento |
| Enfants invisibles (`Not Visible Individually`) | Jamais eu d'URL publique sur Magento |
| Produit actif mais hors scope de la boutique | Absent du catalogue de cette boutique — pas de page cible |

---

## Structure des URLs

### Magento (avant)

```
/{url_key}.html                    → page produit
/{url_path}.html                   → alias (parfois avec suffixe numérique)
/{category-slug}.html              → page catégorie
```

### Shopify (après)

```
/products/{handle}                 → fiche produit
/collections/{collection-handle}   → page collection
```

---

## Types de redirections

### 1. Produits grouped → produit Shopify

L'URL du parent Magento redirige vers le même handle Shopify :

```
/stiga-allround-classic.html  →  /products/stiga-allround-classic
```

> Pas de perte SEO : le Handle Shopify = le url_key Magento. La redirection ne sert
> qu'à gérer le `.html` en fin d'URL.

### 2. url_path avec suffixe numérique

Magento ajoute parfois un suffixe numérique au `url_path` pour éviter les doublons
(ex: `-303`, `-457`). Ces URLs alternatives doivent aussi rediriger :

```
/stiga-allround-classic-wrb-flared-303.html  →  /products/stiga-allround-classic-wrb-flared
```

### 4. Catégories → Collections

```
/blades.html        →  /collections/blades
/rubbers.html       →  /collections/rubbers
/clothing.html      →  /collections/clothing
/shoes.html         →  /collections/shoes
/tables-nets.html   →  /collections/tables-nets
```

> **Prérequis :** les collections Shopify doivent être créées avec les handles correspondants
> avant d'activer ces redirections.

---

## Fichier généré

```
03_SEO_AND_REDIRECTS/shopify_redirects_dandoy.csv
03_SEO_AND_REDIRECTS/shopify_redirects_butterfly.csv
```

Format Matrixify Redirects — colonnes exactes attendues (voir
[matrixify.app/documentation/redirects](https://matrixify.app/documentation/redirects/)) :

| Colonne | Description | Exemple |
|---|---|---|
| `ID` | Vide pour une création (Matrixify assigne l'ID à l'import) | *(vide)* |
| `Path` | Ancien chemin (relatif) | `/stiga-allround-classic-anatomic.html` |
| `Command` | `NEW` pour les fichiers d'import, `DELETE` pour les fichiers PURGE | `NEW` |
| `Target` | Nouveau chemin Shopify | `/products/stiga-allround-classic` |

> ⚠️ Matrixify n'utilise **pas** les en-têtes `Redirect From` / `Redirect To` (erreur
> précédente dans `generate_redirects.py`, corrigée le 06/08/2026) — avec ces mauvais noms de
> colonnes, Matrixify ne reconnaît pas le fichier et renvoie *"Cannot understand the uploaded
> file"*. Les colonnes correctes sont `ID, Path, Command, Target`.

### Import via Matrixify

1. Le fichier doit contenir "Redirects" dans le nom
2. Importer **après** l'import des produits (les URLs cibles doivent exister), dans la
   boutique correspondante (`_dandoy` → boutique Dandoy-Sports, `_butterfly` → boutique Butterfly TT)
3. Matrixify créera des redirections 301 dans **Settings → Navigation → URL Redirects** de
   chaque boutique

---

## Limites Shopify

| Limite | Valeur | Notre situation |
|---|---|---|
| Redirections max (Basic/Shopify) | 100 000 | 2 045 (Dandoy) / 380 (Butterfly) — OK |
| Redirections max (Plus) | 200 000 | OK |
| Taille import Matrixify | 20 Go | ~150 Ko / ~30 Ko — OK |

---

## Ce qui n'est PAS couvert

| Élément | Raison | Action |
|---|---|---|
| Produits avec `url_key` localisé différent (FR/NL) | `generate_redirects.py` ne génère les redirections qu'à partir de l'`url_key` de la vue de base (store view vide) | Voir « URLs produits localisées (FR/NL) » ci-dessous |
| Catégories traduites (ex. `/bois.html`, `/palettes.html`) | Colonne `categories` vide sur **toutes** les store views hors base dans l'export Magento — aucune donnée source pour générer les slugs FR/NL | À faire **manuellement** (voir ci-dessous) |
| Pages CMS Magento | Pas dans l'export produits | Crawl séparé nécessaire |
| URLs avec paramètres (`?color=red`) | Shopify ne redirige pas les query strings | Géré côté serveur ou `.htaccess` si proxy |
| Domaines par boutique (6 domaines / 2 boutiques) | Résolu — Option B retenue | Configurer les domaines dans chaque boutique Shopify (DNS), pas de Shopify Markets nécessaire côté Butterfly |
| Bundle products (105) | Non exportés vers Shopify | URLs en 404 sauf si traitement manuel |

### URLs produits localisées (FR/NL) — audit du 10/08/2026

Comparaison de l'`url_key` par store view vs l'`url_key` de base, restreinte aux produits
actifs et dans le scope de chaque boutique :

| Store view | Boutique | Langue | Produits actifs concernés |
|---|---|---|---|
| `bt_be_fr` | Butterfly TT | FR | **125** |
| `eu_fr` | Dandoy-Sports | FR | 1 (`butterfly-t-shirt-player-red` → `-rouge`, produit partagé) |
| `ww_en` | Dandoy-Sports | EN (`.com`) | 1 (`ZZZ-111-1`, probable produit de test) |
| `eu_en`, `eu_nl`, `bt_be_nl`, `bt_nl` | — | EN/NL | 0 |

Le gros du trou est **Butterfly FR** (`be.butterfly.tt`) : 125 anciennes URLs `.html` en français
ne redirigent vers rien avec le script actuel et finiront en 404 après migration. Le NL n'est
quasiment pas concerné (0 partout). Décision : traitement manuel, pas d'extension du script pour
l'instant.

### Catégories traduites — pas de donnée source

Toutes les redirections de catégories générées (`/blades.html`, `/rubbers.html`, `/clothing.html`…)
sont en **anglais uniquement**, car l'export `export_magento_products_all.csv` n'a jamais
d'`categories` renseignées sur les store views FR/NL (`eu_fr`, `eu_nl`, `bt_be_fr`, `bt_be_nl`,
`bt_nl`) — seule la vue de base (store view vide) porte cette colonne. Si le site live utilise
des slugs de catégorie traduits (ex. `/bois.html` pour Blades en FR), ils ne sont couverts par
**aucune** redirection actuelle, faute de source de données exploitable dans cet export.

**Décision : à faire manuellement** (pas de crawl ni de script automatisé prévu pour l'instant) —
lister les URLs de catégorie FR/NL réellement utilisées sur le site live et créer les
redirections correspondantes directement dans Shopify Admin (Settings → Navigation → URL
Redirects) après import, plutôt que via Matrixify.

---

## Workflow recommandé (dans chaque boutique)

1. **Importer les produits** (`shopify_products_dandoy.csv` ou `shopify_products_butterfly.csv`)
2. **Créer les collections** avec les bons handles (blades, rubbers, clothing…)
3. **Importer les redirections** (`shopify_redirects_dandoy.csv` ou `_butterfly.csv`) via Matrixify
4. **Tester** : vérifier un échantillon d'anciennes URLs Magento → 301 → page Shopify, sur chaque domaine
5. **Crawl post-migration** : utiliser Screaming Frog ou similaire pour détecter les 404 résiduels, sur les 6 domaines

---

## Script

```
02_ANALYSIS_AND_MAPPING/SCRIPTS/generate_redirects.py
```

Régénérable à tout moment depuis l'export Magento brut.
