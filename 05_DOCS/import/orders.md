# Historique des commandes — Magento → Shopify

---

## Données source

| Fichier | Lignes | Contenu |
|---|---|---|
| `export-orders.csv` | 125 436 | Commandes 2015-2025 — résumé sans détail produits |
| `export_order_all_2025_2026.csv` | 37 430 | Commandes 2025-2026 — **avec line items** (SKU, prix, qté) |

---

## Fichier 2015-2025 — Résumé

### Période et volume

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

### Limites

Export de type **résumé** — ne contient pas le détail des produits achetés (SKU, quantités, prix unitaires).

---

## Fichier 2025-2026 — Avec line items

### Période et volume

1 janvier 2025 → 25 juin 2026 — **18 mois**.

### Répartition par store

| Store | Commandes |
|---|---|
| Dandoy EU Français | 11 634 |
| Butterfly BE Français | 9 573 |
| Dandoy WW English | 5 230 |
| Dandoy EU Nederlands | 4 851 |
| Butterfly NL | 3 131 |
| Dandoy EU English | 2 108 |
| Butterfly BE Nederlands | 903 |

### Statistiques

| Donnée | Valeur |
|---|---|
| CA total | 4 853 153 € |
| Panier moyen | 130 € |
| Commandes | 37 430 |
| Line items total | 99 821 |
| Items/commande | moy. 2,7 — médiane 2 — max 56 |
| Financial status paid | 35 194 (94%) |
| Financial status pending | 2 236 (6%) |

### Méthodes de paiement

| Méthode | Commandes |
|---|---|
| Mollie — CB | 16 040 |
| Mollie — PayPal | 7 396 |
| Mollie — Bancontact | 6 636 |
| Mollie — iDEAL | 4 503 |
| PayPlug (CB + iDEAL + Bancontact) | 2 238 |
| PayPal Express | 244 |
| Klarna | 344 |
| Gratuit | 29 |

### Saisonnalité

| Mois | Commandes |
|---|---|
| Novembre 2025 | 3 963 (pic Black Friday) |
| Décembre 2025 | 3 198 (Noël) |
| Janvier 2025/2026 | ~2 500 |
| Juillet (creux) | 1 452 |

### Données disponibles par commande

| Colonne | Disponible |
|---|---|
| ID commande, date, store | ✅ |
| Email client | ✅ |
| Montant total, sous-total, frais de port | ✅ |
| Méthode de paiement, livraison (description) | ✅ |
| **SKU produit** | ✅ (jusqu'à 56 items) |
| **Nom produit, prix unitaire, quantité** | ✅ |
| **Taxes et remises par item** | ✅ |
| Adresse (rue, ville, CP, pays) | ❌ |
| Téléphone | ❌ |

---

## Liaison commandes ↔ clients

Matrixify lie les commandes aux comptes clients via l'email.

| Situation | Commandes | Comportement Shopify |
|---|---|---|
| Email présent dans `shopify_customers.csv` | ~23 500 (52,5%) | Lié au compte client |
| Guest checkout (pas de compte Magento) | ~13 900 (47,5%) | Commande guest — normal |

Les 47,5% sans compte correspondent aux `Customer Group` vide ou `NOT LOGGED IN` — commandes passées sans inscription.
Seulement 7 commandes proviennent de clients enregistrés absents du fichier customers (cas limites).

---

## Options de migration

### Option 1 — Ne pas migrer (Fresh start)

Ne pas importer l'historique des commandes dans Shopify.

**Avantages :** import plus simple, Shopify repart propre.

**Inconvénients :** pas d'historique visible pour le client ni le support.

**Mitigation :** garder l'admin Magento accessible en lecture seule pendant 1-2 ans.

### Option 2 — Import résumé 2015-2025 (sans line items)

Importer les 125 436 commandes avec montant, date, statut, email — sans les produits achetés.

**Résultat :** historique visible dans l'espace client, mais sans les articles (pas de réachat en un clic).

**Limite :** Matrixify **Enterprise** requis (125 436 > limite Big à 10 000).

### Option 3 — Import complet 2025-2026 (avec line items) ✅

Importer les 37 430 commandes récentes avec le détail complet des produits.

**Résultat :** les clients voient leurs achats récents avec les produits dans leur espace client.
Le support peut identifier ce qui a été acheté.

**Limite :** adresses de livraison non disponibles dans l'export.
Les 18 mois couvrent l'essentiel des commandes en cours de garantie ou de SAV.

**Script :** `magento_to_shopify_orders.py` → `shopify_orders.csv` (99 821 lignes).

### Option 4 — Combiné (2 + 3)

Importer d'abord le résumé 2015-2025 (Option 2), puis le détail 2025-2026 (Option 3).
Les deux exports couvrent des périodes différentes — pas de doublon à condition de filtrer.

---

## Script de conversion

```bash
python3 02_ANALYSIS_AND_MAPPING/SCRIPTS/magento_to_shopify_orders.py
```

Inclus dans `regenerate_all.sh` (étape 5/7).

| Champ Magento | Champ Shopify (Matrixify) | Traitement |
|---|---|---|
| `Increment Id` | `Name` | Tel quel (`WEB2-0125-4250`) |
| `Created At` | `Created at` | → ISO 8601 `2025-01-01 02:12:20 +0100` |
| `Payment Method` | `Payment Method` | `mollie_methods_bancontact` → `Bancontact` |
| `Store Name` | `Tags` | `Dandoy*` → `dandoy` / `Butterfly*` → `butterfly` |
| `Total Due = 0` | `Financial Status` | → `paid` / `> 0` → `pending` |
| `item N(Status) = Shipped` | `Lineitem fulfillment status` | → `fulfilled` |
| `item N(Tax Percent)` | `Lineitem taxable` | `TRUE` si taux > 0 |

Format de sortie : **1 ligne par line item** (format long Matrixify).
La première ligne de chaque commande contient tous les champs d'en-tête.
Les lignes suivantes ne contiennent que `Name` + les champs de l'item.

---

## Recommandation

**Option 3 (import 2025-2026 avec line items)** — les 18 mois les plus utiles opérationnellement,
avec les produits achetés visibles dans Shopify.

Conserver l'admin Magento en lecture seule pour l'historique antérieur à 2025.

---

## Décision requise

| Question | Options |
|---|---|
| Importer l'historique ? | Option 1 / 2 / 3 / 4 |
| Garder Magento en lecture seule ? | Oui (recommandé) / Non |
