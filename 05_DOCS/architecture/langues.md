# Gestion des langues et traductions — Dandoy-Sports / Butterfly TT

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

## Workflow d'export recommandé

### Étape 1 — Import produits (fichier principal)

Le fichier `shopify_products.csv` existant importe les produits en **anglais** (langue par défaut).

### Étape 2 — Export traductions (fichier séparé)

Le script `magento_to_shopify.py` génère automatiquement `shopify_translations.csv`
au format Matrixify Translations.

**Logique de sourcing :**
- **FR** : `bt_be_fr` en priorité (traduction Butterfly propre), fallback `eu_fr` (Dandoy)
- **NL** : `eu_nl` (source principale unique)

**Résultat du dernier export :**

| Champ | Lignes | Avec FR | Avec NL |
|---|---|---|---|
| `title` | 2 717 | 2 683 | 1 697 |
| `body_html` | 4 006 | 3 997 | 3 103 |
| **Total** | **6 723** | **4 492 produits** | **3 417 produits** |

### Étape 3 — Import dans Shopify

1. Importer `shopify_products.csv` (produits en anglais + metafields)
2. Activer les langues FR et NL dans **Settings → Languages**
3. Importer `shopify_translations.csv` (traductions FR + NL)

---

## Cas particulier : Butterfly FR

Les produits Butterfly ont leur propre traduction FR dans `bt_be_fr` (5 191 produits).

### Option A — Instance unique

Si Dandoy et Butterfly partagent une seule boutique Shopify :
- Shopify ne supporte qu'**une seule traduction FR** par produit
- Pour les 199 produits partagés (35 actifs) : prioriser `bt_be_fr` ou `eu_fr` (les différences sont mineures)
- **Recommandation** : utiliser `eu_fr` comme source FR principale, les 6 différences de noms sont négligeables

### Option B — Deux boutiques

Chaque boutique a ses propres traductions :
- **Dandoy** : FR = `eu_fr`, NL = `eu_nl`
- **Butterfly** : FR = `bt_be_fr` (avec fallback `eu_fr` pour les produits non traduits), NL = `eu_nl`

---

## Couverture des traductions

### Ce qui sera traduit (sur 4 834 produits exportés)

| Contenu | FR | NL |
|---|---|---|
| Noms de produits (title) | 2 683 (55%) | 1 697 (35%) |
| Descriptions (body_html) | 3 997 (83%) | 3 103 (64%) |
| **Produits avec au moins 1 champ traduit** | **4 492 (93%)** | **3 417 (71%)** |

### Ce qui restera en anglais (fallback)

- ~342 produits sans aucune traduction FR → affichés en anglais
- ~1 417 produits sans aucune traduction NL → affichés en anglais
- Métadonnées SEO (meta_title, meta_description) → quasi vides dans toutes les langues, non exportées

> **Action post-migration :** prioriser la traduction des produits actifs (product_online = 1)
> sans traduction. Les produits draft (désactivés) peuvent rester en anglais.

---

## Sources

- [Matrixify Translations documentation](https://matrixify.app/documentation/translations/)
- [Shopify Translate & Adapt app](https://apps.shopify.com/translate-and-adapt)
