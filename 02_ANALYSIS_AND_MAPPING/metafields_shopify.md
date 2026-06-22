# Metafields Shopify — Dandoy-Sports / Butterfly TT

Définitions des custom metafields à créer dans Shopify Admin
(**Settings → Custom data → Products → Add definition**) pour l'import Matrixify.

---

## Metafields globaux (tous types de produits)

| Namespace.Key | Nom affiché | Type Shopify | Valeurs possibles | Source Magento |
|---|---|---|---|---|
| `custom.promotion` | Promotion | Single line text | Liquidation, NEW, promo, solde, 2 = 3, 3 = 4 | `promotion_type` |

---

## Blades (Bois)

| Namespace.Key | Nom affiché | Type Shopify | Valeurs possibles | Source Magento |
|---|---|---|---|---|
| `custom.blade_category` | Catégorie bois | Single line text | ALL, ALL+, ALL-, DEF, DEF+, OFF, OFF+, OFF- | `blades_type` |
| `custom.blade_layers` | Nombre de plis | Single line text | 1, 3, 3+2, 4, 4+1, 5, 5+2, 5+4, 6+2, 7, 11, 17 | `blades_layers` |
| `custom.blade_feeling` | Sensation | Single line text | hard, medium, soft | `blades_feeling` |
| `custom.technology` | Technologie | List of single line text | Stiga-WRB-system, Stiga-CR-system, Donic-senso, Arylate-carbon, ZL Carbon, Super ZLC, Tamca 5000, Inner Fiber… | `technology_stiga` + `technology_butterfly` |

> **Options de variantes (non metafield) :** `baldes_handles` → **Option1 = Handle** (Anatomic, Flared, Straight, Master, Penholder, Left-Handed, Right-Handed)

---

## Rubbers (Revêtements)

| Namespace.Key | Nom affiché | Type Shopify | Valeurs possibles | Source Magento |
|---|---|---|---|---|
| `custom.rubber_category` | Catégorie revêtement | Single line text | ALL, ALL+, ALL-, DEF, DEF+, OFF, OFF+, OFF- | `rubbers_type` |
| `custom.pimples` | Type de picots | Single line text | Pimple in, Short pimple, Long pimple, Anti | `rubbers_pimples` |
| `custom.hardness` | Dureté | Single line text | Hard, Medium, Soft | `rubbers_hardness` |
| `custom.technology` | Technologie | List of single line text | *(partagé avec Blades, voir ci-dessus)* | `technology_stiga` + `technology_butterfly` |

> **Options de variantes (non metafield) :** `color` → **Option1 = Color** (Red, Black, Blue, Green, Pink, Purple) · `rubbers_thickness` → **Option2 = Thickness** (1.7, 1.9, 2.1, 2.3…)

---

## Clothing (Textiles)

| Namespace.Key | Nom affiché | Type Shopify | Valeurs possibles | Source Magento |
|---|---|---|---|---|
| `custom.gender` | Genre | List of single line text | Man, Woman, Child, Unisex | `gender` (séparateur `\|`) |
| `custom.technology` | Technologie | List of single line text | Breathable, Skin Friendly, Comfortable Stretch, UV Protection, Wicking and Quickdry, Windproof, Anti-Odor | `technology_butterfly` |

> **Options de variantes (non metafield) :** `size` → **Option1 = Size** (XXS, XS, S, M, L, XL, XXL, 3XL, 4XL, 5XL)

---

## Shoes (Chaussures)

| Namespace.Key | Nom affiché | Type Shopify | Valeurs possibles | Source Magento |
|---|---|---|---|---|
| `custom.shoe_type` | Type de chaussure | Single line text | Interior, Exterior, Exterior\|Interior | `shoes_type` |
| `custom.gender` | Genre | List of single line text | *(partagé avec Clothing)* | `gender` |

> **Options de variantes (non metafield) :** `size_shoes` → **Option1 = Size** (36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46)

---

## Bags (Sacs)

| Namespace.Key | Nom affiché | Type Shopify | Valeurs possibles | Source Magento |
|---|---|---|---|---|
| `custom.bag_model` | Modèle de sac | Single line text | Sportbag, Trolleybag, BatcoverSimple, BatwalletDouble, BatwalletSimple, AluCase, backpack | `bags_model` |

> **Options de variantes (non metafield) :** `color` → **Option1 = Color** (Black, Blue, Green, Grey, Red, Orange…)

---

## Balls (Balles)

| Namespace.Key | Nom affiché | Type Shopify | Valeurs possibles | Source Magento |
|---|---|---|---|---|
| `custom.ball_usage` | Usage | Single line text | Competition, Training, Fun | `balls_usage` |
| `custom.ball_material` | Matériau | Single line text | Plastic, Celluloid | `balls_material` |

> **Options de variantes (non metafield) :** `balls_quantity` → **Option1 = Quantity** (3, 6, 10, 12, 30, 72, 100, 120, 144) · `color` → **Option2 = Color** (White, Orange)

---

## Rackets (Raquettes)

| Namespace.Key | Nom affiché | Type Shopify | Valeurs possibles | Source Magento |
|---|---|---|---|---|
| `custom.usage` | Usage | Single line text | Leisure, Pro | `usage` |
| `custom.rubber_category` | Catégorie revêtement | Single line text | *(partagé avec Rubbers)* | `rubbers_type` |
| `custom.environment` | Environnement | Single line text | Indoor, Outdoor | `tables_type` |
| `custom.technology` | Technologie | List of single line text | *(partagé)* | `technology_stiga` |

> **Options de variantes (non metafield) :** Aucune option structurée — fallback sur le suffixe du nom produit → **Option1 = Title**

---

## Tables and Nets (Tables et Filets)

| Namespace.Key | Nom affiché | Type Shopify | Valeurs possibles | Source Magento |
|---|---|---|---|---|
| `custom.environment` | Environnement | Single line text | Indoor, Outdoor | `tables_type` |
| `custom.usage` | Usage | Single line text | Leisure, Pro | `usage` |
| `custom.cover_included` | Housse incluse | Boolean | true / false | `cover` (Yes/No) |
| `custom.dimension` | Dimensions | Single line text | ex: 1600 x 810 x 1580 mm | `dimension` |

> **Options de variantes (non metafield) :** Aucune option structurée — fallback sur le suffixe du nom produit → **Option1 = Title**

---

## Accessories (Accessoires)

| Namespace.Key | Nom affiché | Type Shopify | Valeurs possibles | Source Magento |
|---|---|---|---|---|
| `custom.accessory_type` | Type d'accessoire | Single line text | Edge Tape, Glue, Protectors Sheets, Headbands, Caps, Overgrips, Keychains… | `accessories` |

> **Options de variantes (non metafield) :** Aucune option structurée — fallback sur le suffixe du nom produit → **Option1 = Title**

---

## Cleaners (Nettoyants)

*(Pas de metafield spécifique)*

> **Options de variantes (non metafield) :** `quantity` → **Option1 = Quantity** (25ml, 37ml, 90ml, 100ml, 125ml, 250ml, 500ml, 1l)

---

## Robots

*(Pas de metafield spécifique)*

> **Options de variantes (non metafield) :** Aucune option structurée — fallback sur le suffixe du nom produit → **Option1 = Title**

---

## Clubs

*(Pas de metafield spécifique)*

> **Options de variantes (non metafield) :** Aucune option structurée — fallback sur le suffixe du nom produit → **Option1 = Title**

---

## Divers

| Namespace.Key | Nom affiché | Type Shopify | Valeurs possibles | Source Magento |
|---|---|---|---|---|
| `custom.video_url` | Vidéo produit | URL | URLs YouTube | `videos` |

---

## Récapitulatif : 19 metafields uniques

| # | Namespace.Key | Type | Partagé entre |
|---|---|---|---|
| 1 | `custom.promotion` | Single line text | Tous |
| 2 | `custom.blade_category` | Single line text | Blades |
| 3 | `custom.blade_layers` | Single line text | Blades |
| 4 | `custom.blade_feeling` | Single line text | Blades |
| 5 | `custom.rubber_category` | Single line text | Rubbers, Rackets |
| 6 | `custom.pimples` | Single line text | Rubbers |
| 7 | `custom.hardness` | Single line text | Rubbers |
| 8 | `custom.technology` | List of single line text | Blades, Rubbers, Clothing, Rackets |
| 9 | `custom.gender` | List of single line text | Clothing, Shoes |
| 10 | `custom.shoe_type` | Single line text | Shoes |
| 11 | `custom.bag_model` | Single line text | Bags |
| 12 | `custom.ball_usage` | Single line text | Balls |
| 13 | `custom.ball_material` | Single line text | Balls |
| 14 | `custom.usage` | Single line text | Rackets, Tables |
| 15 | `custom.accessory_type` | Single line text | Accessories |
| 16 | `custom.environment` | Single line text | Rackets, Tables |
| 17 | `custom.cover_included` | Boolean | Tables |
| 18 | `custom.dimension` | Single line text | Tables |
| 19 | `custom.video_url` | URL | Blades, Rubbers, Shoes |

---

## Format CSV (Matrixify)

Les colonnes metafields dans le CSV d'import suivent la convention Matrixify :

```
Metafield: namespace.key [type]
```

Exemples :
- `Metafield: custom.blade_category [single_line_text_field]`
- `Metafield: custom.technology [list.single_line_text_field]`
- `Metafield: custom.cover_included [boolean]`

Pour les types **list**, les valeurs multiples sont séparées par `;` dans la cellule CSV.

---

## Utilisation dans Shopify

### Filtrage (Search & Discovery)
Les metafields suivants sont recommandés comme filtres dans l'app **Shopify Search & Discovery** :

- **Blades** : blade_category, blade_feeling, blade_layers
- **Rubbers** : rubber_category, pimples, hardness
- **Clothing / Shoes** : gender
- **Tables** : environment, usage
- **Tous** : promotion

> **Note — Couleur et Taille :** Les attributs `color`, `size` et `size_shoes` ne sont
> **pas** des metafields mais des **options de variantes** (Option1, Option2). Shopify Search
> & Discovery permet de filtrer nativement sur les options de variantes — il n'est donc pas
> nécessaire de les dupliquer en metafields. Cela s'applique aussi à `baldes_handles`,
> `balls_quantity` et `quantity`.

### Affichage fiche produit
Ajouter via le **Theme Editor** (Customize → Product page → Add block → Metafield) :
- `custom.technology` — liste de technologies
- `custom.dimension` — dimensions pour tables
- `custom.video_url` — vidéo YouTube embarquée
