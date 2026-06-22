# Bundle Products Magento → Shopify — Dandoy-Sports

---

## État des lieux

| Statut | Nombre | Action |
|---|---|---|
| Actifs (`product_online=1`) | 21 | À traiter |
| Désactivés (`product_online=2`) | 84 | Ignorer |
| **Total** | **105** | |

---

## Analyse des bundles actifs

### Pattern "3=4" — Achetez 3, recevez 4 (17 bundles)

Le client choisit **4 revêtements** dans une gamme de produits (ex: toute la série Donic Desto F)
et paie le prix de 3 (prix fixe du bundle = 3 × prix unitaire).

Exemples :

| Bundle | Prix bundle | Prix unitaire | Économie |
|---|---|---|---|
| Donic Desto F serie 3=4 | 119,70 € | 39,90 € | 1 revêtement gratuit |
| Tibhar Evolution Serie 3=4 | 161,70 € | 53,90 € | 1 revêtement gratuit |
| Donic Vario Serie 3=4 | 107,70 € | 35,90 € | 1 revêtement gratuit |
| Stiga Calibra LT Serie 3=4 | 128,70 € | 42,90 € | 1 revêtement gratuit |
| Donic Bluefire M Serie 3=4 | 158,70 € | 52,90 € | 1 revêtement gratuit |

**Structure Magento :** chaque bundle contient la liste complète des variantes éligibles
(toutes couleurs × toutes épaisseurs), répétée 4 fois (une fois par "slot" de sélection).
Les produits référencés existent déjà comme produits simples dans le catalogue.

### Autres bundles (4 bundles)

Bundles divers avec 3-4 articles, même logique de prix fixe réduit.

---

## Solutions dans Shopify

### Solution 1 — Remises automatiques (recommandée pour les "3=4")

**Shopify natif : Settings → Discounts → Create discount → Automatic**

Configuration :
- Type : "Buy X get Y"
- Règle : acheter 3 articles dans une collection, obtenir le 4ème gratuit
- Ciblage : créer une collection par série de produits (ex: "Donic Desto F Serie")
- Application : automatique au panier

**Avantages :**
- Natif Shopify, gratuit, aucune app
- Les produits individuels sont déjà migrés — pas de nouveau produit à créer
- Facile à activer/désactiver
- Visible dans le panier (le client voit la remise)

**Inconvénients :**
- Pas de page produit dédiée au bundle (le client doit ajouter 4 produits au panier)
- Nécessite une collection par série pour cibler les bons produits

**Mise en oeuvre :**
1. Créer une collection par série de bundle (ex: `donic-desto-f-serie`)
2. Y assigner les produits éligibles (déjà migrés)
3. Créer un discount automatique "Buy 3 Get 1 Free" sur cette collection

### Solution 2 — App Shopify Bundles (gratuite)

**App native Shopify** disponible dans l'App Store.

Le bundle apparaît comme un **produit Shopify** où le client choisit les composants.
Le stock des composants est décrémenté automatiquement.

**Avantages :**
- Gratuit (app officielle Shopify)
- Page produit dédiée au bundle
- Gestion du stock liée aux composants
- Le client voit le bundle comme un seul produit

**Inconvénients :**
- Moins flexible que Magento pour les sélections multiples
- Limité en nombre de composants et options

**Adapté pour :** les 4 bundles divers (petits packs avec peu de choix).

### Solution 3 — App tierce (Wide Bundles, Bundle Bear)

Apps spécialisées qui reproduisent fidèlement le comportement Magento :
le client sélectionne N produits dans une liste et paie un prix fixe.

**Avantages :**
- Interface "pick from list" comme sur Magento
- Prix fixe ou remise calculée
- Page produit dédiée avec sélection visuelle

**Inconvénients :**
- Coût mensuel (~15-30 $/mois)
- Dépendance à une app tierce

**Adapté pour :** reproduire exactement l'expérience Magento si c'est un critère.

### Solution 4 — Ne pas migrer

Les bundles "3=4" sont des **promotions commerciales**, pas du catalogue permanent.
Les produits individuels sont déjà migrés. Les promos peuvent être recréées
manuellement dans Shopify quand le besoin se présente.

---

## Recommandation

| Type de bundle | Nombre | Solution | Effort |
|---|---|---|---|
| "3=4" rubbers | 17 | **Remise automatique** Shopify | ~30 min (1 discount par série) |
| Bundles divers | 4 | **Shopify Bundles app** ou recréation manuelle | Ponctuel |
| Bundles désactivés | 84 | **Ignorer** | Rien |

**Aucune migration data nécessaire.** Les produits composant les bundles sont déjà
dans `shopify_products.csv`. La configuration des remises et bundles se fait
directement dans l'admin Shopify après l'import.

---

## Liste des 21 bundles actifs

| SKU | Nom | Type | Prix |
|---|---|---|---|
| 3=4_150 | Donic Desto F serie 3=4 | Rubbers 3=4 | 119,70 € |
| 3=4_21333 | Tibhar Evolution Serie 3=4 | Rubbers 3=4 | 161,70 € |
| 3=4_1506 | Donic Vario Serie 3=4 | Rubbers 3=4 | 107,70 € |
| 3=4_11566 | Stiga Calibra LT Serie 3=4 | Rubbers 3=4 | 128,70 € |
| 3=4_11919 | Donic Bluefire M Serie 3=4 | Rubbers 3=4 | 158,70 € |
| *(+ 12 autres séries 3=4)* | | Rubbers 3=4 | |
| *(+ 4 bundles divers)* | | Divers | |
