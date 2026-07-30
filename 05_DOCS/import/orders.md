# Historique des commandes — Magento → Shopify

> **Deux boutiques Shopify (Option B)** : contrairement aux produits et clients, une commande
> n'appartient qu'à **un seul** store Magento d'origine — elle est donc écrite dans un seul des
> deux fichiers de sortie, jamais dupliquée. `magento_to_shopify_orders.py` route chaque
> commande via `Store Name` (voir mapping ci-dessous).

---

## Données source

| Fichier | Lignes | Contenu |
|---|---|---|
| `export_order_all_2025_2026.csv` | 37 430 | Commandes jan 2025–juin 2026 avec line items (SKU, prix, qté) |

---

## Analyse du fichier

### Période et volume

1 janvier 2025 → 25 juin 2026 — **18 mois**.

### Répartition par store Magento → boutique Shopify cible

| Store Magento | Commandes | Boutique Shopify |
|---|---|---|
| Dandoy EU Français | 11 634 | Dandoy-Sports |
| Butterfly BE Français | 9 573 | Butterfly TT |
| Dandoy WW English | 5 230 | Dandoy-Sports |
| Dandoy EU Nederlands | 4 851 | Dandoy-Sports |
| Butterfly NL | 3 131 | Butterfly TT |
| Dandoy EU English | 2 108 | Dandoy-Sports |
| Butterfly BE Nederlands | 903 | Butterfly TT |

**Total : 23 823 commandes → `shopify_orders_dandoy.csv` / 13 607 commandes → `shopify_orders_butterfly.csv`.**

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

Pic en **novembre-décembre** (Black Friday + Noël) : 3 963 + 3 198 commandes. Creux en juillet (1 452).

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

Matrixify lie les commandes aux comptes clients via l'email, **dans la boutique
correspondante** (une commande `shopify_orders_dandoy.csv` se lie à un client présent dans
`shopify_customers_dandoy.csv`, et de même pour Butterfly).

| Situation | Commandes | Comportement Shopify |
|---|---|---|
| Email présent dans le fichier clients de la même boutique | ~23 500 (52,5%) | Lié au compte client |
| Guest checkout (pas de compte Magento) | ~13 900 (47,5%) | Commande guest — normal |

Les 47,5% sans compte correspondent aux commandes passées sans inscription (`NOT LOGGED IN`).
Seulement 7 commandes proviennent de clients enregistrés absents du fichier customers (cas limites).

---

## Script de conversion

```bash
python3 02_ANALYSIS_AND_MAPPING/SCRIPTS/magento_to_shopify_orders.py
```

Inclus dans `regenerate_all.sh` (étape 5/8). Génère les deux fichiers de sortie en une seule exécution.

Sortie :
- `04_SHOPIFY_IMPORTS/shopify_orders_dandoy.csv` — **71 096 lignes** (23 823 commandes)
- `04_SHOPIFY_IMPORTS/shopify_orders_butterfly.csv` — **28 725 lignes** (13 607 commandes)

Format long Matrixify, 1 ligne par item.

### Mapping des champs

| Champ Magento | Champ Shopify (Matrixify) | Traitement |
|---|---|---|
| `Increment Id` | `Name` | Tel quel (`WEB2-0125-4250`) |
| `Created At` | `Created at` | → ISO 8601 `2025-01-01 02:12:20 +0100` |
| `Payment Method` | `Payment Method` | `mollie_methods_bancontact` → `Bancontact` |
| `Store Name` | `Tags` **+ fichier de sortie** | `Dandoy*` → tag `dandoy`, écrit dans `shopify_orders_dandoy.csv` / `Butterfly*` → tag `butterfly`, écrit dans `shopify_orders_butterfly.csv` |
| `Total Due = 0` | `Financial Status` | → `paid` / `> 0` → `pending` |
| `item N(Status) = Shipped` | `Lineitem fulfillment status` | → `fulfilled` |
| `item N(Tax Percent)` | `Lineitem taxable` | `TRUE` si taux > 0 |

### Format de sortie

La première ligne de chaque commande contient tous les champs d'en-tête.
Les lignes suivantes ne contiennent que `Name` + les champs de l'item.

---

## Import dans Shopify

Via Matrixify, dans chaque boutique : **Import → feuille Orders** → uploader
`shopify_orders_dandoy.csv` (boutique Dandoy-Sports) ou `shopify_orders_butterfly.csv`
(boutique Butterfly TT).

**Vérification après import :**
- Ouvrir une commande dans Shopify Admin → Orders
- Vérifier les items, le montant, le statut
- Vérifier la liaison avec le compte client (si email connu)
