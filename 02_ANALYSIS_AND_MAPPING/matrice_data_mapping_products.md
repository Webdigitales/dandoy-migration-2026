# Matrice de mapping — Produits Magento → Shopify

Correspondance complète entre les champs de l'export Magento et les colonnes du CSV Shopify (format Matrixify).

---

## Champs produit (première ligne par Handle)

| Donnée Source (Magento) | Logique de Transformation | Donnée Cible (Shopify / Matrixify) |
|---|---|---|
| `url_key` (produit parent) | Identifiant unique, répété sur chaque ligne de variante | **Handle** |
| `name` (produit parent) | Injecté uniquement sur la première ligne | **Title** |
| `description` (parent) | Retours à la ligne convertis en `<br>` | **Body (HTML)** |
| `additional_attributes` → `manufacturer` | Extraction de la clé `manufacturer` | **Vendor** |
| `attribute_set_code` | Préfixe `Migration_` supprimé (ex: `Migration_Blades` → `Blades`) | **Type** |
| `categories` | Chaque segment de la catégorie → tag + tags sous-catégories ajoutés | **Tags** |
| `product_online` | `1` → `active`, `2` → `draft` | **Status** |
| `product_online` | `1` → `TRUE`, `2` → `FALSE` | **Published** |
| `meta_title` | Tel quel (fallback sur `name` si vide) | **SEO Title** |
| `meta_description` | Tel quel | **SEO Description** |
| `base_image` + `additional_images` | Préfixe `https://www.dandoy-sports.com/pub/media/catalog/product` ajouté | **Image Src** + **Image Position** |
| — | Toujours `FALSE` | **Gift Card** |

## Champs variante (une ligne par variante)

| Donnée Source (Magento) | Logique de Transformation | Donnée Cible (Shopify / Matrixify) |
|---|---|---|
| `sku` (produit simple/enfant) | Tel quel — correspondance au caractère près avec le stock | **Variant SKU** |
| `price` | Si `special_price` existe : prix promo → Variant Price, prix normal → Compare At | **Variant Price** |
| `special_price` | Voir ci-dessus | **Variant Compare At Price** |
| `weight` | Converti de kg en grammes (× 1000) | **Variant Grams** |
| `qty` | Arrondi à l'entier | **Variant Inventory Qty** |
| `allow_backorders` | `1` → `continue`, autre → `deny` | **Variant Inventory Policy** |
| `tax_class_name` | Non vide → `TRUE`, vide → `FALSE` | **Variant Taxable** |
| — | Toujours `shopify` | **Variant Inventory Tracker** |
| — | Toujours `manual` | **Variant Fulfillment Service** |
| — | Toujours `TRUE` | **Variant Requires Shipping** |

## Options de variantes

| Type produit (attribute_set) | Option1 Name | Source Option1 | Option2 Name | Source Option2 |
|---|---|---|---|---|
| Blades | Handle | `baldes_handles` (nettoyé : `handle-ANATOMIC` → `Anatomic`) | — | — |
| Rubbers | Color | `color` (`.title()`) | Thickness | Partie numérique du suffixe du nom |
| Clothing | Size | `size` | — | — |
| Shoes | Size | `size_shoes` (préfixe `EU` supprimé) | — | — |
| Bags | Color | `color` (`.title()`) | — | — |
| Balls | Quantity | `balls_quantity` | Color | `color` (omis si vide) |
| Cleaners | Quantity | `quantity` | — | — |
| Tables and Nets | Color | Suffixe du nom (ex: `Blue`, `Green`) | — | — |
| Autres | Title | Suffixe du nom (nom enfant − nom parent) | — | — |

## Metafields (19 colonnes)

| Source Magento (`additional_attributes`) | Colonne Matrixify | Type |
|---|---|---|
| `promotion_type` | `Metafield: custom.promotion [list.single_line_text_field]` | List |
| `blades_type` | `Metafield: custom.blade_category [single_line_text_field]` | Text |
| `blades_layers` | `Metafield: custom.blade_layers [single_line_text_field]` | Text |
| `blades_feeling` | `Metafield: custom.blade_feeling [single_line_text_field]` | Text |
| `rubbers_type` | `Metafield: custom.rubber_category [single_line_text_field]` | Text |
| `rubbers_pimples` | `Metafield: custom.pimples [single_line_text_field]` | Text |
| `rubbers_hardness` | `Metafield: custom.hardness [single_line_text_field]` | Text |
| `technology_stiga` + `technology_butterfly` | `Metafield: custom.technology [list.single_line_text_field]` | List (fusionnés, `\|` → `;`) |
| `gender` | `Metafield: custom.gender [list.single_line_text_field]` | List (`\|` → `;`) |
| `shoes_type` | `Metafield: custom.shoe_type [list.single_line_text_field]` | List (`\|` → `;`) |
| `bags_model` | `Metafield: custom.bag_model [single_line_text_field]` | Text |
| `balls_usage` | `Metafield: custom.ball_usage [single_line_text_field]` | Text |
| `balls_material` | `Metafield: custom.ball_material [single_line_text_field]` | Text |
| `usage` | `Metafield: custom.usage [single_line_text_field]` | Text |
| `accessories` | `Metafield: custom.accessory_type [single_line_text_field]` | Text |
| `tables_type` | `Metafield: custom.environment [single_line_text_field]` | Text |
| `cover` | `Metafield: custom.cover_included [boolean]` | Boolean (`Yes` → `true`) |
| `dimension` | `Metafield: custom.dimension [single_line_text_field]` | Text |
| `videos` | `Metafield: custom.video_url [url]` | URL |

## Tags sous-catégories

| Catégorie Magento | Tag ajouté |
|---|---|
| `Clothing/Polos` | `polos` |
| `Clothing/Shorts` | `shorts` |
| `Clothing/T-shirts` | `t-shirts` |
| `Clothing/Jackets` | `jackets` |
| `Clothing/Socks` | `socks` |
| `Clothing/Suits` | `suits` |
| `Clothing/Sweater` | `sweater` |
| `Luggages/Bags` | `bags` |
| `Luggages/Batcover` | `batcover` |
| `Tables & Nets/Tables` | `tables` |
| `Tables & Nets/Nets` | `nets` |
| `Cleaners & Glue/Cleaners` | `cleaners` |
| `Cleaners & Glue/Glue` | `glue` |
| `Rubbers/Colours rubbers` | `colours-rubbers` |
| `Robots/Robots` | `robots-machines` |
| `Robots/Accessories` | `robots-accessories` |
| `Accessories/Rackets` | `accessories-rackets` |
| `Accessories/Textiles` | `accessories-textiles` |
| `Accessories/Robots` | `accessories-robots` |
| `Liquidations Football/Maillot` | `football-maillot` |
| `Liquidations Football/Short` | `football-short` |
| `Liquidations Football/Bas` | `football-bas` |

## Champs Magento ignorés

| Champ | Raison |
|---|---|
| `store_view_code` | Géré via le fichier traductions séparé |
| `product_websites` | Géré via tags `brand:dandoy` / `brand:butterfly` (si option A) |
| `configurable_variations` | Non utilisé (produits grouped, pas configurable) |
| `bundle_values` | Bundles gérés via remises Shopify, pas de migration data |
| `custom_options` | Géré via line item properties dans le thème |
| `related_skus` / `crosssell_skus` / `upsell_skus` | À reconfigurer manuellement dans Shopify |
