# Contraintes Techniques — Migration Shopify

Contraintes techniques identifiées lors de l'analyse du catalogue Magento,
hors gestion des stocks (voir [Guide prestataire stock](./stock/guide-prestataire.md)).

---

## 1. Architecture catalogue — Grouped Products

### Le problème

Sur Magento, les produits à variantes (ex: une raquette avec plusieurs types de manches)
ont été configurés en **Grouped Products** au lieu de Configurable Products.

Un Grouped Product Magento = un produit parent + des produits simples indépendants liés.
Chaque simple a son propre SKU, prix, stock, et URL.

### La solution appliquée

Le script de conversion restructure les données :

- Le `url_key` du produit parent → **Handle** Shopify
- Chaque produit simple enfant → une **variante** Shopify
- Les attributs de `additional_attributes` → **options** Shopify (Option1, Option2, Option3)

### Mapping des options par type

| Type produit | Option1 | Option2 | Source Magento |
|---|---|---|---|
| Blades | Handle (Anatomic, Flared…) | — | `baldes_handles` |
| Rubbers | Color (Red, Black…) | Thickness (1.7, 2.1…) | `color` + suffixe nom |
| Clothing | Size (XS→5XL) | — | `size` |
| Shoes | Size (36→46) | — | `size_shoes` |
| Bags | Color | — | `color` |
| Balls | Quantity (3, 12, 72…) | Color (si dispo) | `balls_quantity` + `color` |
| Cleaners | Quantity (100ml, 250ml…) | — | `quantity` |
| Autres | Title (suffixe du nom) | — | Fallback automatique |

> **Attention :** si une option est déclarée (ex: Color) mais sans valeur pour un produit,
> elle est omise. Shopify refuse les options avec nom mais sans valeur.

---

## 2. Limite des 100 variantes par produit

Shopify limite à **100 variantes** et **3 options** par produit.
Cette limite s'applique à tous les plans (y compris Plus).

### Audit du catalogue

| Variantes par produit | Nombre de produits |
|---|---|
| 1–5 | 1 881 |
| 6–10 | 1 613 |
| 11–20 | 425 |
| 21–50 | 3 |
| 51–99 | 0 |
| 100+ | **0** |

**Maximum constaté : 33 variantes** (textiles Joola). Aucun produit ne dépasse la limite.
Pas de scission nécessaire.

---

## 3. Custom options (hors variantes)

Magento utilise des "custom options" (checkbox, radio) qui ne créent pas de variante
et n'impactent pas le SKU. Shopify n'a pas d'équivalent natif.

| Option | Type | Produits | Impact prix | Solution Shopify |
|---|---|---|---|---|
| **Gluing** (Forehand/Backhand) | Radio | 4 009 revêtements | Gratuit | Line item property |
| **Edge tape** (Dandoy/Donic/Stiga) | Radio | 342 revêtements | Gratuit | Line item property |
| **Lacquering** | Checkbox | 976 bois | Gratuit | Line item property |
| **Option de livraison** | Radio | 33 tables | **41–116 €** | App tierce |

Les line item properties nécessitent un ajout de code dans le thème Liquid
(voir [Custom options](./mapping/custom-options.md) pour le code).

L'option de livraison des tables nécessite une **app tierce** (Bold Product Options
ou équivalent) car elle impacte le prix.

---

## 4. Bundles (promotions "3=4")

105 bundles Magento dont 21 actifs. Ce sont des **promotions commerciales**,
pas des produits composés. Les produits individuels existent déjà dans le catalogue.

| Type | Nombre | Solution |
|---|---|---|
| Promo "3=4" rubbers | 17 | Remise automatique Shopify (Buy 3 Get 1 Free) |
| Bundles divers | 4 | App Shopify Bundles (gratuit) |
| Désactivés | 84 | Ignorer |

Pas de migration data nécessaire. Voir [Bundles](./mapping/bundles.md).

---

## 5. Multi-sites et langues

### 6 domaines, 3 langues

| Domaine | Catalogue | Langues |
|---|---|---|
| `dandoy-sports.com` | 4 258 produits (2 033 actifs) | EN, FR, NL |
| `fr/en/nl.dandoy-sports.eu` | Même catalogue | FR, EN, NL |
| `be.butterfly.tt` | 880 produits (350 actifs) | FR, NL |
| `nl.butterfly.tt` | 881 produits (351 actifs) | NL |

199 produits sont **partagés** entre Dandoy et Butterfly (35 actifs).

### Store views obsolètes

| Store view | Raison |
|---|---|
| `eu_en_old` | Remplacée par `eu_en`, à ne pas migrer |
| `bt_be_en` | Non utilisée, à ne pas migrer |

### Traductions

| Langue | Couverture | Source Magento |
|---|---|---|
| Anglais | 100% (défaut) | Store view `(base)` |
| Français | 93% des produits | `eu_fr` (Dandoy) + `bt_be_fr` (Butterfly) |
| Néerlandais | 71% des produits | `eu_nl` |

Les produits sans traduction s'affichent en anglais (fallback).

Voir [Gestion des langues](./architecture/langues.md) et [Multi-sites](./architecture/multi-sites.md).

---

## 6. Images

Les URLs images pointent vers le serveur Magento :

```
https://www.dandoy-sports.com/pub/media/catalog/product/...
```

**Contraintes :**

- Le site Magento **doit rester en ligne** pendant l'import Matrixify
  (Shopify télécharge les images au moment de l'import)
- Formats supportés : JPEG, PNG, GIF, WebP
- Les images sont sur le produit parent (grouped) — les variantes héritent de l'image produit

### Images de variantes

Sur Magento, chaque produit simple enfant possède sa propre image (22 993 images distinctes).
Shopify permet d'associer une image par variante via la colonne `Variant Image`.

**Décision actuelle : non activé.** Les Variant Images ne sont pas exportées pour éviter
de doubler la galerie produit (chaque Variant Image est automatiquement ajoutée à la galerie
si elle n'y est pas déjà). Pour un produit Blade avec 5 variantes, ça ajouterait 5 images
en plus des 3 images parent.

**Pour activer ultérieurement :** dans `magento_to_shopify.py`, ajouter avant le bloc
`if option_defs:` dans la section grouped :

```python
child_img = image_url(child.get('base_image', ''))
if child_img:
    out['Variant Image'] = child_img
```

La colonne `Variant Image` est déjà dans les en-têtes CSV — il suffit de décommenter la logique.

---

## 7. SEO — Redirections 301

### Structure des URLs

| Magento | Shopify |
|---|---|
| `/{url_key}.html` | `/products/{handle}` |
| `/{category}.html` | `/collections/{handle}` |

### Redirections générées

| Type | Nombre |
|---|---|
| Produits actifs et visibles | 2 333 |
| Catégories | 35 |
| **Total** | **2 368** |

### Ce qui n'est PAS redirigé

- Produits désactivés (`product_online=2`) → déjà en 404 sur Magento
- Enfants simples (`Not Visible Individually`) → jamais eu d'URL publique
- Pages CMS → crawl séparé nécessaire
- URLs avec paramètres (`?color=red`) → non supporté par les redirections Shopify

Voir [Redirections 301](./import/redirections.md).

---

## 8. Prix

### Prix standard

Le prix Magento (`price`) devient le `Variant Price` Shopify.

### Prix spécial (promotions)

Si `special_price` est renseigné dans Magento :

- `Variant Price` = special_price (prix promo)
- `Variant Compare At Price` = price (prix barré)

Cela affiche automatiquement le prix barré dans Shopify.

### Produits grouped (parents)

Les produits grouped Magento n'ont **pas de prix** au niveau parent.
Le prix est porté par chaque produit simple enfant (= variante Shopify).

---

## 9. Statut des produits

| Magento `product_online` | Shopify `Status` | Visible sur la boutique |
|---|---|---|
| `1` | `active` | Oui |
| `2` | `draft` | Non |

Sur 4 834 produits exportés, environ la moitié sont en draft (désactivés dans Magento).
Ils sont importés pour conservation du catalogue mais ne sont pas visibles côté client.

---

## 10. Metafields

19 metafields custom créés automatiquement par Matrixify à l'import.
À valider dans **Settings → Custom data → Products** après l'import.

Voir [Metafields](./mapping/metafields.md) pour la liste complète.

---

## Récapitulatif des risques

| Risque | Probabilité | Impact | Mitigation |
|---|---|---|---|
| Images inaccessibles pendant l'import | Moyenne | Images manquantes | Garder Magento en ligne jusqu'à la fin de l'import |
| SKU modifié → stock désynchronisé | Faible | Stock incorrect | Ne jamais modifier les SKU |
| Option vide déclarée → erreur Matrixify | Corrigé | Variante non créée | Script corrigé (options vides omises) |
| Produit >100 variantes | Aucune | Bloquant | Audité : max 33, pas de risque |
| Survente produits partagés (si 2 boutiques) | Moyenne | Commande sans stock | Recommandation : instance unique |
