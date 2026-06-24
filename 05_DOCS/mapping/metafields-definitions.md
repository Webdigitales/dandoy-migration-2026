# Metafields — Définitions

Les 19 custom metafields créés automatiquement par Matrixify à l'import.
Référence technique : types, sources Magento, et options de variantes associées.

---

## Récapitulatif

| # | Namespace.Key | Type | Valeur | Filtre Magento | Usage Shopify |
|---|---|---|---|---|---|
| 1 | `custom.promotion` | List of single line text | Multiple | Oui (tous) | Filtre |
| 2 | `custom.blade_category` | Single line text | Simple | Oui (Blades) | Filtre |
| 3 | `custom.blade_layers` | Single line text | Simple | Oui (Blades) | Filtre |
| 4 | `custom.blade_feeling` | Single line text | Simple | Oui (Blades) | Filtre |
| 5 | `custom.rubber_category` | Single line text | Simple | Oui (Rubbers) | Filtre |
| 6 | `custom.pimples` | Single line text | Simple | Oui (Rubbers) | Filtre |
| 7 | `custom.hardness` | Single line text | Simple | Non | Filtre (nouveau) |
| 8 | `custom.technology` | List of single line text | Multiple | Non | Affichage fiche |
| 9 | `custom.gender` | List of single line text | Multiple | Non | Filtre (nouveau) |
| 10 | `custom.shoe_type` | List of single line text | Multiple | Oui (Shoes) | Filtre |
| 11 | `custom.bag_model` | Single line text | Simple | Oui (Luggages) | Filtre |
| 12 | `custom.ball_usage` | Single line text | Simple | Oui (Balls) | Filtre |
| 13 | `custom.ball_material` | Single line text | Simple | Oui (Balls) | Filtre |
| 14 | `custom.usage` | Single line text | Simple | Non | Filtre (nouveau) |
| 15 | `custom.accessory_type` | Single line text | Simple | Non | Filtre (nouveau) |
| 16 | `custom.environment` | Single line text | Simple | Non | Filtre (nouveau) |
| 17 | `custom.cover_included` | Boolean | Simple | Non | Affichage fiche |
| 18 | `custom.dimension` | Single line text | Simple | Non | Affichage fiche |
| 19 | `custom.video_url` | URL | Simple | Non | Affichage fiche |

> **Filtres natifs Shopify** (pas des metafields) : Vendor (= Manufacturer), Price, Color,
> Size, Quantity — ces attributs sont filtrables nativement via Search & Discovery.

---

## Détail par type de produit

### Metafields globaux (tous types)

| Namespace.Key | Nom affiché | Type Shopify | Valeurs possibles | Source Magento |
|---|---|---|---|---|
| `custom.promotion` | Promotion | List of single line text | Liquidation, NEW, promo, solde, 2 = 3, 3 = 4 | `promotion_type` (séparateur `\|`) |

### Blades (Bois)

| Namespace.Key | Nom affiché | Type Shopify | Valeurs possibles | Source Magento |
|---|---|---|---|---|
| `custom.blade_category` | Catégorie bois | Single line text | ALL, ALL+, ALL-, DEF, DEF+, OFF, OFF+, OFF- | `blades_type` |
| `custom.blade_layers` | Nombre de plis | Single line text | 1, 3, 3+2, 4, 4+1, 5, 5+2, 5+4, 6+2, 7, 11, 17 | `blades_layers` |
| `custom.blade_feeling` | Sensation | Single line text | hard, medium, soft | `blades_feeling` |
| `custom.technology` | Technologie | List of single line text | 77 valeurs par marque | `technology_stiga` + `technology_butterfly` |

> **Options de variantes (non metafield) :** `baldes_handles` → **Option1 = Handle** (Anatomic, Flared, Straight, Master, Penholder, Left-Handed, Right-Handed)

### Rubbers (Revêtements)

| Namespace.Key | Nom affiché | Type Shopify | Valeurs possibles | Source Magento |
|---|---|---|---|---|
| `custom.rubber_category` | Catégorie revêtement | Single line text | ALL, ALL+, ALL-, DEF, DEF+, OFF, OFF+, OFF- | `rubbers_type` |
| `custom.pimples` | Type de picots | Single line text | Pimple in, Short pimple, Long pimple, Anti | `rubbers_pimples` |
| `custom.hardness` | Dureté | Single line text | Hard, Medium, Soft | `rubbers_hardness` |
| `custom.technology` | Technologie | List of single line text | *(partagé avec Blades)* | `technology_stiga` + `technology_butterfly` |

> **Options de variantes (non metafield) :** `color` → **Option1 = Color** (Red, Black, Blue, Green, Pink, Purple) · `rubbers_thickness` → **Option2 = Thickness** (1.7, 1.9, 2.1, 2.3…)

### Clothing (Textiles)

| Namespace.Key | Nom affiché | Type Shopify | Valeurs possibles | Source Magento |
|---|---|---|---|---|
| `custom.gender` | Genre | List of single line text | Man, Woman, Child, Unisex | `gender` (séparateur `\|`) |
| `custom.technology` | Technologie | List of single line text | Breathable, Skin Friendly, Comfortable Stretch… | `technology_butterfly` |

> **Options de variantes (non metafield) :** `size` → **Option1 = Size** (XXS, XS, S, M, L, XL, XXL, 3XL, 4XL, 5XL)

### Shoes (Chaussures)

| Namespace.Key | Nom affiché | Type Shopify | Valeurs possibles | Source Magento |
|---|---|---|---|---|
| `custom.shoe_type` | Type de chaussure | List of single line text | Interior, Exterior | `shoes_type` (séparateur `\|`) |
| `custom.gender` | Genre | List of single line text | *(partagé avec Clothing)* | `gender` |

> **Options de variantes (non metafield) :** `size_shoes` → **Option1 = Size** (36→46)

### Bags (Sacs)

| Namespace.Key | Nom affiché | Type Shopify | Valeurs possibles | Source Magento |
|---|---|---|---|---|
| `custom.bag_model` | Modèle de sac | Single line text | Sportbag, Trolleybag, BatcoverSimple, BatwalletDouble, BatwalletSimple, AluCase, backpack | `bags_model` |

> **Options de variantes (non metafield) :** `color` → **Option1 = Color**

### Balls (Balles)

| Namespace.Key | Nom affiché | Type Shopify | Valeurs possibles | Source Magento |
|---|---|---|---|---|
| `custom.ball_usage` | Usage | Single line text | Competition, Training, Fun | `balls_usage` |
| `custom.ball_material` | Matériau | Single line text | Plastic, Celluloid | `balls_material` |

> **Options de variantes (non metafield) :** `balls_quantity` → **Option1 = Quantity** · `color` → **Option2 = Color** (si disponible)

### Rackets (Raquettes)

| Namespace.Key | Nom affiché | Type Shopify | Valeurs possibles | Source Magento |
|---|---|---|---|---|
| `custom.usage` | Usage | Single line text | Leisure, Pro | `usage` |
| `custom.rubber_category` | Catégorie revêtement | Single line text | *(partagé avec Rubbers)* | `rubbers_type` |
| `custom.environment` | Environnement | Single line text | Indoor, Outdoor | `tables_type` |
| `custom.technology` | Technologie | List of single line text | *(partagé)* | `technology_stiga` |

### Tables and Nets

| Namespace.Key | Nom affiché | Type Shopify | Valeurs possibles | Source Magento |
|---|---|---|---|---|
| `custom.environment` | Environnement | Single line text | Indoor, Outdoor | `tables_type` |
| `custom.usage` | Usage | Single line text | Leisure, Pro | `usage` |
| `custom.cover_included` | Housse incluse | Boolean | true / false | `cover` (Yes/No) |
| `custom.dimension` | Dimensions | Single line text | ex: 1600 x 810 x 1580 mm | `dimension` |

### Accessories

| Namespace.Key | Nom affiché | Type Shopify | Valeurs possibles | Source Magento |
|---|---|---|---|---|
| `custom.accessory_type` | Type d'accessoire | Single line text | Edge Tape, Glue, Protectors Sheets, Headbands, Caps… | `accessories` |

### Divers

| Namespace.Key | Nom affiché | Type Shopify | Valeurs possibles | Source Magento |
|---|---|---|---|---|
| `custom.video_url` | Vidéo produit | URL | URLs YouTube | `videos` |

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
