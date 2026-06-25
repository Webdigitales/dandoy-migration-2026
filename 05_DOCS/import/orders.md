# Historique des commandes — Magento → Shopify

---

## Données source

| Fichier Magento | Lignes | Contenu |
|---|---|---|
| `export-orders.csv` | 125 436 | Commandes (résumé, sans détail des produits) |

### Période couverte

Août 2015 → Septembre 2025 — **10 ans d'historique**.

### Répartition par source

| Purchase Point | Commandes |
|---|---|
| Dandoy WW (anglais) | 32 858 |
| Dandoy EU (français) | 31 560 |
| Butterfly BE (français) | 20 959 |
| Dandoy EU (néerlandais) | 15 648 |
| Butterfly NL | 12 829 |
| Dandoy EU (anglais) | 7 319 |
| Butterfly BE (néerlandais) | 3 870 |

### Statistiques

| Donnée | Valeur |
|---|---|
| CA total | 83,8 M€ |
| Panier moyen | 668 € |
| Statut Complete | 125 129 (99,8%) |
| Statut Closed | 99 |
| Statut Processing | 12 |
| Statut Canceled | 3 |

### Méthodes de paiement

| Méthode | Commandes |
|---|---|
| Credit Cards | 38 438 |
| ops_cc (Ogone) | 20 611 |
| Bancontact | 19 951 |
| PayPal | 18 041 |
| iDeal / Wero | 17 656 |
| Klarna | 396 |
| Point of Sale | 9 |

---

## Limites de l'export disponible

L'export Magento actuel est un **résumé de commandes** — il ne contient pas le détail
des produits achetés.

| Colonne disponible | Colonne manquante |
|---|---|
| ID commande | SKU des produits achetés |
| Date, statut | Quantités par produit |
| Montant total | Prix unitaires |
| Email client | Détail des remises |
| Adresse facturation/livraison | Numéros de suivi |
| Méthode de paiement | Taxes détaillées |
| Frais de port | |

Pour un import complet avec le détail des produits, il faudrait un export Magento
de type **Sales → Orders** avec les lignes de commande (order items).

---

## Options de migration

### Option 1 — Ne pas migrer (Fresh start)

Ne pas importer l'historique des commandes dans Shopify.

**Avantages :**
- Import plus simple et plus rapide
- Moins de risques d'erreurs
- Shopify repart propre

**Inconvénients :**
- L'équipe support ne peut pas consulter les anciennes commandes dans Shopify
- Les clients ne voient pas leur historique d'achat dans leur espace client

**Mitigation :** garder l'admin Magento accessible en lecture seule pendant 1-2 ans
pour les consultations de l'historique.

### Option 2 — Import résumé (avec l'export disponible)

Importer les commandes avec les données disponibles : montant, date, statut, email.
Sans le détail des produits.

**Résultat dans Shopify :** les commandes apparaissent dans l'historique client
avec le montant total, mais sans les lignes de produits.

**Limites :**
- Pas de réachat en un clic depuis l'historique
- Pas de filtrage par produit acheté
- Matrixify **Enterprise** requis (125 436 commandes > limite Big à 10 000)

### Option 3 — Import complet (nécessite un nouvel export)

Exporter depuis Magento un fichier avec les **order items** (produits par commande),
puis créer un script de conversion vers le format Matrixify orders.

**Format Matrixify orders requis :**

```
Name, Email, Financial Status, Fulfillment Status, Currency,
Lineitem name, Lineitem quantity, Lineitem price, Lineitem sku,
Billing Name, Billing Address1, Billing City, Billing Country,
Shipping Name, Shipping Address1, Shipping City, Shipping Country,
Created at, ...
```

---

## Recommandation

**Option 1 (Fresh start)** pour commencer, avec Magento en lecture seule.

Les commandes les plus récentes (2024-2025) peuvent être importées manuellement
si nécessaire. L'historique complet reste consultable sur Magento.

Si l'import de l'historique est décidé ultérieurement, demander à Magento
un export avec les order items et relancer un script de conversion.

---

## Décision requise

| Question | Options |
|---|---|
| Importer l'historique ? | Oui (résumé) / Oui (complet) / Non (fresh start) |
| Si oui : garder Magento accessible ? | Oui (lecture seule) / Non |
| Période à importer ? | Tout (2015→2025) / Derniers 2 ans / Dernière année |
