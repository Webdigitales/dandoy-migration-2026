# Redirections 301 — Migration Magento → Shopify

> **Deux boutiques Shopify (Option B)** : chaque boutique n'a besoin de rediriger que les
> produits/catégories effectivement présents dans son catalogue. `generate_redirects.py`
> scope automatiquement chaque redirection à la bonne boutique via `product_websites`
> (fonction `brand_scope()`, partagée avec `magento_to_shopify.py`) — voir `multi_sites_shopify.md`.

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

Format Matrixify Redirects :

| Colonne | Description | Exemple |
|---|---|---|
| `Redirect From` | Ancien chemin (relatif) | `/stiga-allround-classic-anatomic.html` |
| `Redirect To` | Nouveau chemin Shopify | `/products/stiga-allround-classic` |

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
| URLs traduites (`/fr/`, `/nl/`) | Seules 18 URL keys FR existent dans Magento, pas significatif | À gérer manuellement si nécessaire |
| Pages CMS Magento | Pas dans l'export produits | Crawl séparé nécessaire |
| URLs avec paramètres (`?color=red`) | Shopify ne redirige pas les query strings | Géré côté serveur ou `.htaccess` si proxy |
| Domaines par boutique (6 domaines / 2 boutiques) | Résolu — Option B retenue | Configurer les domaines dans chaque boutique Shopify (DNS), pas de Shopify Markets nécessaire côté Butterfly |
| Bundle products (105) | Non exportés vers Shopify | URLs en 404 sauf si traitement manuel |

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
