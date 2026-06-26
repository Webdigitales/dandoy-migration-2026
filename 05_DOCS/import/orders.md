# Historique des commandes — Magento → Shopify

---

## Données source

| Fichier | Lignes | Contenu |
|---|---|---|
| `export_order_all_2025_2026.csv` | 37 430 | Commandes jan 2025–juin 2026 avec line items (SKU, prix, qté) |

---

## Analyse du fichier

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

Matrixify lie les commandes aux comptes clients via l'email.

| Situation | Commandes | Comportement Shopify |
|---|---|---|
| Email présent dans `shopify_customers.csv` | ~23 500 (52,5%) | Lié au compte client |
| Guest checkout (pas de compte Magento) | ~13 900 (47,5%) | Commande guest — normal |

Les 47,5% sans compte correspondent aux commandes passées sans inscription (`NOT LOGGED IN`).
Seulement 7 commandes proviennent de clients enregistrés absents du fichier customers (cas limites).

---

## Script de conversion

```bash
python3 02_ANALYSIS_AND_MAPPING/SCRIPTS/magento_to_shopify_orders.py
```

Inclus dans `regenerate_all.sh` (étape 5/7).

Sortie : `04_SHOPIFY_IMPORTS/shopify_orders.csv` — **99 821 lignes** (format long Matrixify, 1 ligne par item).

### Mapping des champs

| Champ Magento | Champ Shopify (Matrixify) | Traitement |
|---|---|---|
| `Increment Id` | `Name` | Tel quel (`WEB2-0125-4250`) |
| `Created At` | `Created at` | → ISO 8601 `2025-01-01 02:12:20 +0100` |
| `Payment Method` | `Payment Method` | `mollie_methods_bancontact` → `Bancontact` |
| `Store Name` | `Tags` | `Dandoy*` → `dandoy` / `Butterfly*` → `butterfly` |
| `Total Due = 0` | `Financial Status` | → `paid` / `> 0` → `pending` |
| `item N(Status) = Shipped` | `Lineitem fulfillment status` | → `fulfilled` |
| `item N(Tax Percent)` | `Lineitem taxable` | `TRUE` si taux > 0 |

### Format de sortie

La première ligne de chaque commande contient tous les champs d'en-tête.
Les lignes suivantes ne contiennent que `Name` + les champs de l'item.

---

## Import dans Shopify

Via Matrixify : **Import → feuille Orders** → uploader `shopify_orders.csv`.

**Vérification après import :**
- Ouvrir une commande dans Shopify Admin → Orders
- Vérifier les items, le montant, le statut
- Vérifier la liaison avec le compte client (si email connu)
