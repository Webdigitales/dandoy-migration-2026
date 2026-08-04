# Historique des commandes — Magento → Shopify

> **Deux boutiques Shopify (Option B)** : contrairement aux produits et clients, une commande
> n'appartient qu'à **un seul** store Magento d'origine — elle est donc écrite dans un seul des
> deux fichiers de sortie, jamais dupliquée. `magento_to_shopify_orders.py` route chaque
> commande via `Store Name` (voir mapping ci-dessous).

---

## Données source

| Fichier | Lignes | Contenu |
|---|---|---|
| `export_order_all_2025_2026.csv` | 39 051 commandes | Commandes jan 2025–aujourd'hui avec line items (SKU, prix, qté), adresses billing/shipping |

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

**Total : 24 855 commandes → `shopify_orders_dandoy.csv` / 14 196 commandes → `shopify_orders_butterfly.csv`.**

### Statistiques

| Donnée | Valeur |
|---|---|
| CA total | 5 094 918 € |
| Panier moyen | 130,47 € |
| Commandes | 39 051 |
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
| Date d'expédition réelle | ❌ — voir [Fulfillment](#fulfillment-des-commandes-expédiées) |
| Point relais (bpost/DPD/Sendcloud), ID transaction Mollie | ❌ — demandé, voir [Champ Note](#champ-note) |

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
- `04_SHOPIFY_IMPORTS/shopify_orders_dandoy.csv` — **99 135 lignes** (24 855 commandes)
- `04_SHOPIFY_IMPORTS/shopify_orders_butterfly.csv` — **44 149 lignes** (14 196 commandes)

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

- **99,2 % des commandes** (38 722/39 051) ont tous leurs items à `Status = Shipped` → une
  ligne `Fulfillment Line` par commande (`Fulfillment: Status = success`,
  `Fulfillment: Send Receipt = FALSE` pour ne pas ré-notifier les clients par email).
- Les **0,8 % restants** (statuts `Invoiced`/`Mixed`) restent non expédiées plutôt que de
  deviner un état incertain.
- `Fulfillment: Processed At` (date d'expédition historique) est **laissé vide** : aucune
  date fiable disponible côté export Magento actuel (`Bpost Drop/Delivery Date` ne couvre que
  18 % des commandes — bpost est loin d'être le seul transporteur ; `Created At` est la date
  de commande, pas d'expédition). `Updated At` a été demandé côté export Magento (couvre
  100 % des commandes) — une fois ajouté, le script le reprendra automatiquement.

> ⚠️ **Non testé en live** — contrairement au reste du mapping commandes, ce mécanisme n'a
> pas encore été validé par un import Matrixify réel. À vérifier au prochain test sample.

### Champ Note

`Note` est actuellement vide. Objectif : y placer le point relais (bpost/DPD/Sendcloud) et
l'ID de transaction Mollie, utiles au support client. Colonnes Magento disponibles mais
**absentes de l'export actuel** — demandées le 4 août 2026 :

| Donnée | Colonnes Magento à ajouter à l'export |
|---|---|
| Point relais bpost | `bpost_point_office`, `bpost_point_street`, `bpost_point_nr`, `bpost_point_zip`, `bpost_point_city` |
| Point relais DPD | `dpd_parcelshop_name`, `dpd_parcelshop_street`, `dpd_parcelshop_house_number`, `dpd_parcelshop_zip_code`, `dpd_parcelshop_city` |
| Point relais Sendcloud | `sendcloud_service_point_name`, `sendcloud_service_point_street`, `sendcloud_service_point_house_number`, `sendcloud_service_point_zip_code`, `sendcloud_service_point_city` |
| Transaction Mollie | `mollie_transaction_id` |

Une commande n'aura qu'un seul type de point relais rempli (selon le transporteur choisi) —
le script essaiera bpost → DPD → Sendcloud dans cet ordre.

**Question ouverte côté PayPlug/PayPal Express (~2 500 commandes, 6,4 % du volume, méthodes
`payplug_payments_*` et `paypal_express`)** : seul `mollie_transaction_id` apparaît dans la
liste d'attributs Magento actuellement disponible — pas d'équivalent visible pour ces deux
passerelles. Possible que l'ID de transaction y soit stocké hors des attributs order plats
(`sales_order_payment.additional_information`), non accessible via ce type d'export. Question
posée au prestataire/dev Magento le 4 août 2026 ; à défaut de réponse, `Note` restera vide
pour ces commandes.

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
