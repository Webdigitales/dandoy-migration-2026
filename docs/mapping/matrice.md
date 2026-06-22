# Matrice de mapping — Produits Magento → Shopify

| Donnée Source (Magento) | Logique de Transformation / Nettoyage | Donnée Cible (Shopify / Matrixify) |
|---|---|---|
| `url_key` (du produit Parent) | Identifiant unique répété sur chaque ligne de variante | **Handle** |
| `name` (du produit Parent) | Injecté uniquement sur la première ligne (coquille parente) | **Title** |
| `description` (Parent) | Nettoyage du code HTML obsolète | **Body (HTML)** |
| `sku` (produit Simple/Enfant) | Crucial : doit correspondre au caractère près à l'application de stock | **Variant SKU** |
| `price` / `weight` | Repris des lignes enfants (simple) | **Variant Price** / **Variant Weight** |
| `additional_attributes` | Extraction (ex: `baldes_handles=handle-ANATOMIC` → Option: Manche / Valeur: Anatomique) | **Option 1 Name** / **Option 1 Value** |
