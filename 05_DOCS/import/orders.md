# Historique des commandes — Magento → Shopify

> **Deux boutiques Shopify (Option B)** : contrairement aux produits et clients, une commande
> n'appartient qu'à **un seul** store Magento d'origine — elle est donc écrite dans un seul des
> deux fichiers de sortie, jamais dupliquée. `magento_to_shopify_orders.py` route chaque
> commande via `Store Name` (voir mapping ci-dessous).

---

## Données source

| Fichier | Lignes | Contenu |
|---|---|---|
| `export_order_all_2025_2026.csv` | 39 094 commandes | Commandes jan 2025–aujourd'hui avec line items (SKU, prix, qté), adresses billing/shipping |

---

## Analyse du fichier

### Période et volume

Janvier 2025 → aujourd'hui (période complète, corrigée le 30 juillet 2026 après un premier
export tronqué — voir Historique des commits).

### Répartition par store Magento → boutique Shopify cible

| Store Magento | Commandes | Boutique Shopify |
|---|---|---|
| Dandoy Sports EU Français | 12 129 | Dandoy-Sports |
| Butterfly BE Français | 9 966 | Butterfly TT |
| Dandoy Sports WW English | 5 457 | Dandoy-Sports |
| Dandoy Sports EU Nederlands | 5 077 | Dandoy-Sports |
| Butterfly NL | 3 287 | Butterfly TT |
| Dandoy Sports EU English | 2 192 | Dandoy-Sports |
| Butterfly BE Nederlands | 943 | Butterfly TT |

**Total : 24 896 commandes → `shopify_orders_dandoy.csv` / 14 198 commandes → `shopify_orders_butterfly.csv`.**

### Statistiques

| Donnée | Valeur |
|---|---|
| CA total | 5 094 918 € |
| Panier moyen | 130,47 € |
| Commandes | 39 094 |
| Line items total | 104 562 |
| Items/commande | moy. 2,68 — max 56 |
| Financial status paid | 36 324 (93%) |
| Financial status pending | 2 727 (7%) |

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
| Adresse billing/shipping (rue, ville, CP, pays) | ✅ (14 colonnes ajoutées le 30 juillet 2026) |
| Téléphone | ✅ |
| Statut d'expédition par item (`Shipped`/`Invoiced`/`Mixed`) | ✅ |
| Date d'expédition réelle | ⚠️ approximée par `Updated At` — voir [Fulfillment](#fulfillment-des-commandes-expédiées) |
| Point relais (Sendcloud), ID transaction Mollie | ✅ (89,7 %) — voir [Champ Note](#champ-note) |

---

## Liaison commandes ↔ clients

Matrixify lie les commandes aux comptes clients via l'email, **dans la boutique
correspondante** (une commande `shopify_orders_dandoy.csv` se lie à un client présent dans
`shopify_customers_dandoy.csv`, et de même pour Butterfly).

| Situation | Commandes | Comportement Shopify |
|---|---|---|
| Email présent dans le fichier clients de la même boutique | 23 991 (61,4%) | Lié au compte client |
| Guest checkout / email absent du fichier clients | 15 060 (38,6%) | Commande guest — normal |

---

## Script de conversion

```bash
python3 02_ANALYSIS_AND_MAPPING/SCRIPTS/magento_to_shopify_orders.py
```

Inclus dans `regenerate_all.sh` (étape 5/8). Génère les deux fichiers de sortie en une seule exécution.

Sortie :
- `04_SHOPIFY_IMPORTS/shopify_orders_dandoy.csv` — **99 294 lignes** (24 896 commandes)
- `04_SHOPIFY_IMPORTS/shopify_orders_butterfly.csv` — **44 154 lignes** (14 198 commandes)

Format long Matrixify, 1 ligne par item + 1 ligne `Fulfillment Line` par commande expédiée
(voir [Fulfillment des commandes expédiées](#fulfillment-des-commandes-expédiées)).

### Mapping des champs

Noms de colonnes confirmés via tests d'import Matrixify réels (30 juillet 2026) — Matrixify
mélange deux conventions selon les champs (voir commentaire en tête de
`magento_to_shopify_orders.py` pour l'historique des échecs silencieux qui ont mené à ce mapping) :

| Champ Magento | Champ Shopify (Matrixify) | Traitement |
|---|---|---|
| `Increment Id` | `Name` | Tel quel (`WEB2-0125-4250`) |
| `Created At` | `Created at` | → ISO 8601 `2025-01-01 02:12:20 +0100` |
| `Payment Method` | `Transaction: Payment Method` | `mollie_methods_bancontact` → `Bancontact` |
| `Store Name` | `Tags` **+ fichier de sortie** | `Dandoy*` → tag `dandoy`, écrit dans `shopify_orders_dandoy.csv` / `Butterfly*` → tag `butterfly`, écrit dans `shopify_orders_butterfly.csv` |
| `Total Due` / `Subtotal Refunded` | `Payment: Status` | `refunded` si remboursé, `pending` si dû > 0, sinon `paid` |
| `item N(Tax Percent)` | `Line: Taxable` | `TRUE` si taux > 0 |
| `item N(Tax Amount)` | `Line: Tax 1 Title/Rate/Price` | Repris tel quel par item (voir Fiscalité ci-dessous) |
| `BillingAddress.*` / `ShippingAddress.*` | `Billing: *` / `Shipping: *` | Rue multi-lignes nettoyée (dédoublonnage ville), code pays ISO dans `Country` (pas de colonne `Country Code` dans le template Orders) |

### Fiscalité, remises et devise

Trois bugs corrigés après un premier test d'import live (commande WEB1-0125-17658, Total
Shopify 106,37 € vs 108,45 € réel) :

- **Taxe absente du total** : `Tax: Total` seul ne suffit pas — dès que les line items sont
  eux-mêmes taxables, Matrixify ignore la taxe au niveau commande pour éviter une double
  taxation (doc officielle). Corrigé en répétant la taxe sur chaque ligne via
  `Line: Tax 1 Title/Rate/Price`.
- **Remise TTC vs prix HT** : `Discount Amount` de Magento est TTC alors que `Line: Price`
  est HT — soustraire la remise brute faisait dévier le Total de 2-3 %. Corrigée en HT avant
  soustraction (`Price: Total Discount`).
- **Devise** : 997 commandes (2,5 %, boutique WW hors UE) exportent un `Grand Total` en
  devise locale à côté d'un `Base Grand_total` en EUR, sans code devise explicite dans
  l'export — un taux de change dérivé par commande (`fx_rate()` dans le script) reconvertit
  tous les montants concernés avant l'envoi à Shopify.

### Fulfillment des commandes expédiées

Le statut d'expédition n'est **pas** settable via une colonne sur les lignes `Line Item`
(`Fulfillment Status` / `Line: Fulfillment Status` sont export-only côté Matrixify — testé et
confirmé en échec). Il faut une ligne séparée par commande avec `Line: Type = 'Fulfillment
Line'` — confirmé par la doc officielle Matrixify (contredit une suggestion externe qui
proposait des colonnes directement sur les lignes `Line Item`).

- **99,2 % des commandes** (38 765/39 094) ont tous leurs items à `Status = Shipped` → une
  ligne `Fulfillment Line` par commande (`Fulfillment: Status = success`,
  `Fulfillment: Send Receipt = FALSE` pour ne pas ré-notifier les clients par email).
- Les **0,8 % restants** (statuts `Invoiced`/`Mixed`) restent non expédiées plutôt que de
  deviner un état incertain.
- `Fulfillment: Processed At` (date d'expédition historique) est mappé sur `Updated At`
  (ajouté à l'export Magento le 4 août 2026, 100 % rempli — approximatif, c'est la date de
  dernière modification de la commande, pas une vraie date d'expédition, mais la meilleure
  source disponible). Format source différent de `Created At`
  (`2025-01-02 11:11:43` vs `Jan 1, 2025 02:12:20 AM`) — `parse_date()` reconnaît les deux.
- **`Line: ID` doit rester vide** sur la ligne `Fulfillment Line` — un ID neuf fait que
  Matrixify traite la ligne comme un fulfillment **partiel** référençant ce `Line Item`
  précis (qui n'existe pas), et rejette la commande.
- **`Fulfillment: Shipment Status` obligatoire dès que `Processed At` est rempli** —
  Matrixify refuse la ligne sinon (`"you also need to set the 'Fulfillment: Shipment
  Status' of: 'delivered' or 'failure'"`). Mis à `delivered` (commandes historiques déjà
  expédiées).

> ✅ **Testé en live le 4 août 2026** — 2 essais échoués (`Line: ID` en trop, puis
> `Shipment Status` manquant), corrigés le jour même. À revalider au prochain import
> Matrixify sample.

### Champ Note

Rempli avec le point relais et l'ID de transaction Mollie quand disponibles, ex. :
`Point relais: LOPES WELKENRAEDT RUE DE L EGLISE 24, 4840 WELKENRAEDT | Mollie:
tr_cAMbSG6aTS`. Colonnes ajoutées à l'export Magento le 4 août 2026 :

| Donnée | Colonnes Magento | Taux de remplissage réel |
|---|---|---|
| Point relais bpost | `bpost_point_office`, `bpost_point_street`, `bpost_point_nr`, `bpost_point_zip`, `bpost_point_city` | 0 % — vide dans tout le jeu de données |
| Point relais DPD | `dpd_parcelshop_name`, `dpd_parcelshop_street`, `dpd_parcelshop_house_number`, `dpd_parcelshop_zip_code`, `dpd_parcelshop_city` | 0 % — vide dans tout le jeu de données |
| Point relais Sendcloud | `sendcloud_service_point_name`, `sendcloud_service_point_street`, `sendcloud_service_point_house_number`, `sendcloud_service_point_zip_code`, `sendcloud_service_point_city` | **23,8 %** — seul mécanisme réellement utilisé |
| Transaction Mollie | `mollie_transaction_id` | **89,7 %** |

Une commande n'aura qu'un seul type de point relais rempli — le script essaie bpost → DPD →
Sendcloud dans cet ordre, mais en pratique seul Sendcloud est jamais renseigné (correspond aux
libellés "Point Relais - UPS/DPD/Mondial Relay" dans `Shipping Description` : Sendcloud est
l'intégration meta-transporteur derrière ces méthodes). Les colonnes bpost/DPD sont conservées
en fallback sans coût, au cas où un futur export les remplirait.

**Question ouverte côté PayPlug/PayPal Express/Klarna (~2 850 commandes, 7,3 % du volume,
méthodes `payplug_payments_*`, `paypal_express`, `klarna`)** : seul `mollie_transaction_id`
existe côté Magento — **confirmé absent** pour ces trois passerelles (vérifié directement dans
l'admin Magento le 4 août 2026). Probablement stocké hors des attributs order
plats, dans `sales_order_payment.additional_information` — à vérifier directement en base ;
non accessible via ce type d'export en l'état. À défaut, `Note` restera vide pour ces
commandes.

### Format de sortie

La première ligne de chaque commande contient tous les champs d'en-tête.
Les lignes suivantes ne contiennent que `Name` + les champs de l'item (et la ligne
`Fulfillment Line` finale, qui ne porte que `Name` + ses propres champs).

---

## Import dans Shopify

Via Matrixify, dans chaque boutique : **Import → feuille Orders** → uploader
`shopify_orders_dandoy.csv` (boutique Dandoy-Sports) ou `shopify_orders_butterfly.csv`
(boutique Butterfly TT).

**Vérification après import :**
- Ouvrir une commande dans Shopify Admin → Orders
- Vérifier les items, le montant, le statut
- Vérifier la liaison avec le compte client (si email connu)
