# Règles d'import/export Matrixify — Dandoy-Sports

Référence des règles et contraintes Matrixify pour l'import produits dans Shopify.

---

## Identification des produits

Matrixify identifie un produit par (ordre de priorité) :
1. **ID** Shopify (si le produit existe déjà)
2. **Handle** (= `url_key` Magento dans notre cas)
3. **Variant SKU**

Dans notre CSV, c'est le **Handle** qui relie les lignes d'un même produit.

---

## Commandes d'import (colonne `Command`)

| Commande | Comportement |
|---|---|
| *(vide)* | Équivaut à MERGE |
| **MERGE** | Cherche le produit existant et le met à jour. S'il n'existe pas, le crée. |
| **NEW** | Crée un nouveau produit. Échoue si le Handle existe déjà. |
| **UPDATE** | Met à jour un produit existant. Échoue si le produit n'existe pas. |
| **REPLACE** | Supprime le produit entièrement et le recrée. Toute donnée absente du fichier est perdue. |
| **DELETE** | Supprime le produit. |
| **IGNORE** | Ignore la ligne. |

> **Pour la migration initiale :** laisser la colonne Command vide (= MERGE par défaut).
> Pour les mises à jour ultérieures, utiliser UPDATE pour éviter de créer des doublons.

---

## Structure du fichier CSV

| Règle | Détail |
|---|---|
| **Nommage** | Le fichier doit contenir "Products" dans le nom (ex: `shopify_products.csv`) |
| **Encodage** | UTF-8 (auto-détecté par Matrixify) |
| **Délimiteur** | Virgule `,` — valeurs texte entre guillemets `"` |
| **Ordre des colonnes** | Libre — Matrixify reconnaît les en-têtes. Les colonnes non reconnues sont ignorées. |
| **Regroupement** | Les lignes d'un même produit doivent être **consécutives** (triées par Handle). Dès que le Handle change, Matrixify traite le produit suivant. |
| **Première ligne produit** | Porte toutes les données produit (Title, Body HTML, Vendor, Tags, metafields…) + première variante |
| **Lignes suivantes** | Handle + données variante uniquement (Option values, SKU, Price, Qty…) |

---

## Variantes

- Chaque variante = une ligne avec le même Handle
- Shopify limite à **100 variantes** et **3 options** (Option1, Option2, Option3) par produit
- Sous-commande `Variant Command` :
  - **MERGE** (défaut) : ajoute les nouvelles variantes et met à jour les existantes
  - **REPLACE** : remplace toutes les variantes existantes par celles du fichier (supprime celles absentes)

---

## Images

### Une image par ligne (méthode actuelle)

```csv
Handle,Image Src,Image Position
mon-produit,https://example.com/img1.jpg,1
mon-produit,https://example.com/img2.jpg,2
```

### Plusieurs images par cellule (alternative)

Les images peuvent être regroupées dans une seule cellule `Image Src`, séparées par `;` :

```csv
Handle,Image Src
mon-produit,https://example.com/img1.jpg;https://example.com/img2.jpg;https://example.com/img3.jpg
```

> Cette méthode réduit le nombre de lignes dans le fichier.

### Sous-commande `Image Command`

| Commande | Comportement |
|---|---|
| *(vide)* / **MERGE** | Garde les images existantes + ajoute les nouvelles |
| **REPLACE** | Supprime toutes les images existantes, ne garde que celles du fichier |

### Contraintes images

- L'URL doit être **publique et accessible directement** (pas de redirection, pas de login)
- Shopify télécharge les images au moment de l'import — le serveur source (Magento) doit être en ligne
- Formats supportés : JPEG, PNG, GIF, WebP

---

## Metafields

### Format des colonnes

```
Metafield: namespace.key [type]
```

Exemples :
- `Metafield: custom.blade_category [single_line_text_field]`
- `Metafield: custom.technology [list.single_line_text_field]`
- `Metafield: custom.cover_included [boolean]`

### Metafields de variante

```
Variant Metafield: namespace.key [type]
```

### Création automatique

Matrixify **crée automatiquement** la définition du metafield dans Shopify si elle n'existe pas.
Après l'import, valider les définitions dans **Settings → Custom data → Products** (nom affiché,
description, choix prédéfinis).

### Valeurs list

Pour les types `list.*`, les valeurs multiples sont séparées par `;` dans la cellule :

```
Stiga-WRB-system;Stiga-CR-system
```

---

## Limites techniques

| Limite | Valeur | Note |
|---|---|---|
| Taille max du fichier | 20 Go | Par job d'import |
| Colonnes max | 16 384 | Utiliser CSV si >10 000 colonnes de metafields |
| Caractères par cellule | 32 767 | Attention aux longues descriptions HTML |
| Variantes par produit | 100 | Limite Shopify (pas Matrixify) |
| Options par produit | 3 | Option1, Option2, Option3 |

---

## Conformité de notre fichier

| Règle | Statut |
|---|---|
| Nom contient "Products" | `shopify_products.csv` |
| UTF-8 | Oui |
| Handle comme identifiant | Oui (`url_key` Magento) |
| Lignes consécutives par produit | Oui (grouped + children, puis images) |
| Metafields au format Matrixify | Oui (`Metafield: namespace.key [type]`) |
| Max 3 options | Oui (max 2 utilisées : Color + Thickness) |
| Max 100 variantes | Oui (max constaté : 33) |
| URLs images publiques | Oui (`dandoy-sports.com/pub/media/…`) |

---

## Sources

- [Shopify Products import / export template & guide](https://matrixify.app/documentation/products/)
- [List of Matrixify Commands](https://matrixify.app/documentation/list-of-commands-across-matrixify-sheets/)
- [How to import several product images from one row](https://matrixify.app/tutorials/import-several-product-images-from-one-row/)
- [Metafields documentation](https://matrixify.app/documentation/metafields/)
- [How Matrixify Works](https://matrixify.app/how-it-works/)
