# Metafields — Filtrage & Affichage

Comment les metafields sont utilisés côté client : filtres dans les collections
et affichage sur la fiche produit.

---

## Comparaison avec Magento

Filtres vérifiés sur le site Magento live (dandoy-sports.com) le 24 juin 2026.

### Filtres existants sur Magento (à reproduire)

| Filtre Magento | Catégorie | Solution Shopify | Type |
|---|---|---|---|
| Manufacturer | Tous | **Vendor** (natif) | Natif |
| Price | Tous | **Price** (natif) | Natif |
| MainColor | Rubbers, Clothing, Shoes, Balls, Luggages | **Option de variante** Color (natif) | Natif |
| Size | Clothing | **Option de variante** Size (natif) | Natif |
| Quantity | Balls | **Option de variante** Quantity (natif) | Natif |
| Blade type | Blades | `custom.blade_category` | Metafield |
| Layers | Blades | `custom.blade_layers` | Metafield |
| Blades Feeling | Blades | `custom.blade_feeling` | Metafield |
| Type (rubbers) | Rubbers | `custom.rubber_category` | Metafield |
| Pimples | Rubbers | `custom.pimples` | Metafield |
| Type (shoes) | Shoes | `custom.shoe_type` | Metafield |
| Model | Luggages | `custom.bag_model` | Metafield |
| Material | Balls | `custom.ball_material` | Metafield |
| Usage | Balls | `custom.ball_usage` | Metafield |
| Promotion | Tous | `custom.promotion` | Metafield |
| Category (sous-cat.) | Clothing, Luggages, Rubbers | **Tags** + Smart Collections | Natif |

### Nouveaux filtres (pas sur Magento, possibles sur Shopify)

| Metafield | Catégorie | Intérêt |
|---|---|---|
| `custom.hardness` | Rubbers | Dureté du revêtement (Hard/Medium/Soft) |
| `custom.gender` | Clothing, Shoes | Filtrer par genre (Man/Woman/Child/Unisex) |
| `custom.usage` | Rackets, Tables | Niveau d'utilisation (Leisure/Pro) |
| `custom.environment` | Rackets, Tables | Intérieur/Extérieur |
| `custom.accessory_type` | Accessories | Type d'accessoire |

---

## Configuration Search & Discovery

Aller dans **Apps → Search & Discovery → Filters** pour ajouter les filtres metafield.

### Filtres recommandés par collection

| Collection | Filtres metafield | Filtres natifs |
|---|---|---|
| **Blades** | blade_category, blade_feeling, blade_layers | Vendor, Price |
| **Rubbers** | rubber_category, pimples, hardness | Vendor, Price, Color |
| **Clothing** | gender | Vendor, Price, Size |
| **Shoes** | shoe_type, gender | Vendor, Price, Size |
| **Balls** | ball_usage, ball_material | Vendor, Price, Color, Quantity |
| **Luggages** | bag_model | Vendor, Price, Color |
| **Tables & Nets** | environment, usage | Vendor, Price |
| **Rackets** | usage, environment | Vendor, Price |
| **Accessories** | accessory_type | Vendor, Price |
| **Toutes** | promotion | Vendor, Price |

> **Note — Couleur et Taille :** Les attributs `color`, `size` et `size_shoes` ne sont
> **pas** des metafields mais des **options de variantes** (Option1, Option2). Shopify Search
> & Discovery permet de filtrer nativement sur les options de variantes — il n'est donc pas
> nécessaire de les dupliquer en metafields.

---

## Affichage fiche produit

Ajouter via le **Theme Editor** (Customize → Product page → Add block → source dynamique → Metafield) :

| Metafield | Affichage | Présent sur Magento |
|---|---|---|
| `custom.technology` | Liste de technologies (texte libre, multi-valeurs) | Oui — section "More Information" |
| `custom.dimension` | Dimensions pour tables | Oui |
| `custom.video_url` | Vidéo YouTube embarquée | Non |
| `custom.cover_included` | Housse incluse (Oui/Non) | Non |

> **`custom.technology`** est un champ texte libre (77 valeurs par marque). Il n'est **pas**
> utilisé comme filtre — uniquement pour l'affichage sur la fiche produit, comme sur
> le site Magento actuel.
