# Gestion des langues et traductions — Dandoy-Sports / Butterfly TT

> **Deux boutiques Shopify (Option B, décidée le 29 juillet 2026)** : Dandoy-Sports et
> Butterfly TT gèrent leurs traductions indépendamment, chacune avec son propre fichier
> `shopify_translations_{dandoy|butterfly}.csv`. Voir `multi_sites_shopify.md`.

---

## Situation actuelle sur Magento

### Langue par défaut

Le store view `(base)` contient le contenu en **anglais** — c'est la langue principale du catalogue.

### Traductions disponibles

| Store view | Langue | Noms traduits | Descriptions traduites | Utilisation |
|---|---|---|---|---|
| `eu_fr` | Français | 19 357 | 13 302 | Source FR principale (Dandoy) |
| `eu_nl` | Néerlandais | 17 248 | 11 227 | Source NL principale (Dandoy) |
| `eu_en` | Anglais | 4 | 29 | Quasi vide — overrides prix/promos uniquement |
| `ww_en` | Anglais | 4 | 1 | Overrides prix/promos uniquement |
| `bt_be_fr` | Français | 5 191 | 3 867 | Source FR Butterfly (propre à Butterfly) |
| `bt_be_nl` | Néerlandais | 7 | 56 | Quasi vide |
| `bt_nl` | Néerlandais | 6 | 55 | Quasi vide |

### Constats

1. **Français** : bien couvert via `eu_fr` (Dandoy) et `bt_be_fr` (Butterfly)
2. **Néerlandais** : bien couvert via `eu_nl` (Dandoy). Les vues `bt_be_nl` et `bt_nl` sont quasi vides — elles héritent de `eu_nl` dans Magento
3. **Anglais** : le contenu `(base)` sert de référence. Les vues `eu_en` et `ww_en` ne contiennent quasiment pas de traductions spécifiques
4. **Butterfly FR vs Dandoy FR** : sur les 87 produits partagés avec les deux traductions, 81 ont un nom identique. Les 6 différences sont mineures (ex: "Shirt" vs "Polo")

---

## Stratégie de migration vers Shopify

### Langue par défaut Shopify

**Anglais (en)** — contenu du store view `(base)`.

### Langues secondaires à activer

Activer dans **Settings → Languages** :

| Langue | Code locale | Source Magento |
|---|---|---|
| Français | `fr` | `eu_fr` (Dandoy) / `bt_be_fr` (Butterfly) |
| Néerlandais | `nl` | `eu_nl` (Dandoy) |

> **Note :** les vues Butterfly NL (`bt_be_nl`, `bt_nl`) sont trop incomplètes pour être
> une source de traduction autonome. Elles tombent en fallback sur `eu_nl`.

---

## Import des traductions via Matrixify

Matrixify gère les traductions via un **fichier séparé** du fichier produits principal,
au format "Translations".

### Structure du fichier de traductions

| Colonne | Description | Exemple |
|---|---|---|
| `Entity` | Type d'entité | `Product` |
| `Entity Handle` | Handle du produit | `stiga-allround-classic` |
| `Field` | Champ à traduire | `title`, `body_html` |
| `Translation Value: fr` | Traduction française | `Stiga Allround Classic` |
| `Translation Value: nl` | Traduction néerlandaise | `Stiga Allround Classic` |

### Exemple

```csv
Entity,Entity Handle,Field,Translation Value: fr,Translation Value: nl
Product,stiga-allround-classic,title,Stiga Allround Classic,Stiga Allround Classic
Product,stiga-allround-classic,body_html,"<p>Un bois léger 5 plis…</p>","<p>Een licht 5-laags…</p>"
Product,stiga-airoc-m,title,Stiga Airoc M,Stiga Airoc M
Product,stiga-airoc-m,body_html,"<p>Revêtement offensif…</p>","<p>Offensieve rubber…</p>"
```

### Champs traductibles pour les produits

| Champ Shopify | Source Magento |
|---|---|
| `title` | `name` |
| `body_html` | `description` |
| `meta_title` | `meta_title` (souvent vide) |
| `meta_description` | `meta_description` (souvent vide) |

### Metafields

Les metafields de type texte sont aussi traductibles. Format de colonne :

```
Field = metafield.custom.blade_category
```

---

## Workflow d'export recommandé (par boutique)

### Étape 1 — Import produits (fichier principal)

`shopify_products_dandoy.csv` / `shopify_products_butterfly.csv` importent les produits en
**anglais** (langue par défaut) dans leur boutique respective. Butterfly n'a pas de traduction
EN propre (voir ci-dessous) — l'anglais n'est de toute façon pas activé dans cette boutique.

### Étape 2 — Export traductions (fichier séparé, par boutique)

Le script `magento_to_shopify.py` génère automatiquement
`shopify_translations_dandoy.csv` et `shopify_translations_butterfly.csv`
au format Matrixify Translations.

**Logique de sourcing (identique dans les deux fichiers) :**
- **FR** : `bt_be_fr` en priorité (traduction Butterfly propre), fallback `eu_fr` (Dandoy)
- **NL** : `eu_nl` (source principale unique)

**Résultat du dernier export :**

| Boutique | Lignes traduction | Produits avec FR | Produits avec NL |
|---|---|---|---|
| Dandoy-Sports (4 183 produits) | 5 768 | 3 856 (92%) | 3 417 (82%) |
| Butterfly TT (849 produits) | 1 233 | 809 (95%) | 19 (2%) |

> Le NL de Butterfly est très faible car `bt_be_nl` / `bt_nl` sont quasi vides dans Magento —
> la source NL commune (`eu_nl`) ne couvre que les 199 produits partagés avec Dandoy.

### Étape 3 — Import dans Shopify (dans chaque boutique)

1. Importer `shopify_products_{store}.csv` (produits en anglais + metafields)
2. Activer les langues FR et NL (+ EN pour Dandoy) dans **Settings → Languages**
3. Importer `shopify_translations_{store}.csv` (traductions FR + NL)

---

## Cas particulier : Butterfly FR

Les produits Butterfly ont leur propre traduction FR dans `bt_be_fr` (5 191 produits). Avec
l'**Option B retenue** (deux boutiques séparées), chaque boutique a ses propres traductions,
sans conflit sur les 199 produits partagés (chacun a sa version dans son propre fichier) :

- **Dandoy** : FR = `eu_fr` en priorité, NL = `eu_nl`
- **Butterfly** : FR = `bt_be_fr` en priorité (fallback `eu_fr` pour les produits non traduits), NL = `eu_nl`

---

## Couverture des traductions

### Ce qui sera traduit

| Boutique | Titres traduits | Descriptions traduites | Au moins 1 champ traduit |
|---|---|---|---|
| Dandoy-Sports | — | — | 3 856 / 4 183 (92%) FR, 3 417 / 4 183 (82%) NL |
| Butterfly TT | — | — | 809 / 849 (95%) FR, 19 / 849 (2%) NL |

### Ce qui restera en anglais / non traduit (fallback)

- Dandoy : ~327 produits sans traduction FR, ~766 sans traduction NL → affichés dans la langue par défaut
- Butterfly : ~40 produits sans traduction FR, ~830 sans traduction NL (attendu, voir note ci-dessus) — Butterfly n'active pas l'anglais, ces produits nécessitent une traduction manuelle prioritaire
- Métadonnées SEO (meta_title, meta_description) → quasi vides dans toutes les langues, non exportées

> **Action post-migration :** prioriser la traduction NL des produits actifs Butterfly
> (product_online = 1), c'est le point de couverture le plus faible des deux boutiques.

---

## Sources

- [Matrixify Translations documentation](https://matrixify.app/documentation/translations/)
- [Shopify Translate & Adapt app](https://apps.shopify.com/translate-and-adapt)
