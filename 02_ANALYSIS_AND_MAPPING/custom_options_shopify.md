# Custom Options Magento → Shopify — Dandoy-Sports

Les **custom options** Magento sont des options par produit (checkbox, radio) qui n'impactent
pas le SKU ni le stock. Shopify n'a pas d'équivalent natif — ce document décrit comment
les migrer.

---

## Inventaire des custom options Magento

### Rubbers (Revêtements)

| Option | Type | Requis | Valeurs | Prix | Occurrences |
|---|---|---|---|---|---|
| **Gluing** | Radio | Non | Forehand, Backhand | Gratuit | 4 009 produits |
| **Edge tape** | Radio | Non | Dandoy, Donic, Stiga, Yes, No | Gratuit | 342 produits |
| **Lacquering** | Checkbox | Non | Yes | Gratuit | 6 produits |
| **Collage** | Radio | Non | Coup Droit, Revers | Gratuit | 1 produit |

> **Note :** "Collage" est la version française de "Gluing".

### Blades (Bois)

| Option | Type | Requis | Valeurs | Prix | Occurrences |
|---|---|---|---|---|---|
| **Lacquering** | Checkbox | Non | Yes | Gratuit | 976 produits |

### Rackets (Raquettes)

| Option | Type | Requis | Valeurs | Prix | Occurrences |
|---|---|---|---|---|---|
| **Gluing** | Radio | Non | Yes, No | Gratuit | 20 produits |

### Tables and Nets (Tables et Filets)

| Option | Type | Requis | Valeurs | Prix | Occurrences |
|---|---|---|---|---|---|
| **Option de livraison** | Radio | **Oui** | Enlevée à Ciney, Livrée montée à votre domicile, Livrée à votre domicile | 41 € – 116 € | 31 produits |
| **Delivery option** | Radio | **Oui** | Delivery at home, Pick up in Ciney | 85 € | 2 produits |

---

## Solution recommandée par type

### 1. Gluing / Lacquering / Edge tape — Line item properties

Ces options sont **gratuites, optionnelles** et **informatives** (elles indiquent une
préférence client transmise à l'atelier). La solution native Shopify est le
**line item property**.

#### Principe

Le client sélectionne une valeur sur la fiche produit. La valeur est attachée à la ligne
de commande (visible dans l'admin Shopify, les emails de confirmation et les packing slips)
sans créer de variante ni impacter le stock.

#### Implémentation dans le thème Liquid

Ajouter dans le formulaire produit (`sections/main-product.liquid` ou snippet de formulaire) :

```liquid
{% if product.type == 'Rubbers' %}
  <div class="product-option">
    <label for="gluing">Gluing</label>
    <select name="properties[Gluing]" id="gluing">
      <option value="">— None —</option>
      <option value="Forehand">Forehand</option>
      <option value="Backhand">Backhand</option>
    </select>
  </div>
{% endif %}

{% if product.type == 'Rubbers' %}
  <div class="product-option">
    <label for="edge-tape">Edge tape</label>
    <select name="properties[Edge tape]" id="edge-tape">
      <option value="">— None —</option>
      <option value="Dandoy">Dandoy</option>
      <option value="Donic">Donic</option>
      <option value="Stiga">Stiga</option>
    </select>
  </div>
{% endif %}

{% if product.type == 'Blades' or product.type == 'Rubbers' %}
  <div class="product-option">
    <label>
      <input type="checkbox" name="properties[Lacquering]" value="Yes">
      Lacquering
    </label>
  </div>
{% endif %}
```

#### Résultat dans la commande

```
Stiga Airoc M — Red / 2.1
  Gluing: Forehand
  Lacquering: Yes
```

#### Avantages

- Natif Shopify, aucune app requise
- Pas d'impact sur les variantes ni sur le stock
- Visible dans l'admin, les emails et les exports de commande
- Gratuit

#### Limites

- Demande un ajout de code dans le thème (one-time)
- Pas de logique conditionnelle avancée sans JavaScript
- Non filtrable dans les collections (ce n'est pas un attribut produit)

---

### 2. Option de livraison Tables — App tierce ou Shopify Scripts

L'option de livraison des tables est un cas **différent** : elle est **obligatoire** et
impacte le **prix** (41 € à 116 € de supplément).

#### Approches possibles

| Approche | Avantage | Inconvénient |
|---|---|---|
| **App tierce** (Bold Product Options, Infinite Options) | Interface admin, gestion des prix, conditions | Coût mensuel (~20 $/mois) |
| **Variante Shopify** | Natif, prix intégré | Multiplie les variantes (× 3 options livraison) |
| **Line item property + Shopify Functions** (Plus) | Natif, calcul prix dynamique | Nécessite Shopify Plus + développement custom |
| **Métafield + cart transform** | Flexible | Développement custom |

#### Recommandation

Pour 33 produits tables, la solution la plus pragmatique est l'**app tierce** (Bold Product
Options ou Globo Product Options). Elle permet de :
- Ajouter un sélecteur obligatoire avec prix par option
- Cibler uniquement les produits de type "Tables and Nets"
- Gérer la traduction FR/NL/EN des labels

Alternativement, si ces tables ont peu de variantes, ajouter la livraison comme **variante
Shopify** (Option2 = Livraison) reste envisageable vu le faible volume.

---

## Récapitulatif

| Option | Produits | Prix | Solution Shopify |
|---|---|---|---|
| Gluing (Forehand/Backhand) | Rubbers (4 009) | Gratuit | Line item property |
| Edge tape (Dandoy/Donic/Stiga) | Rubbers (342) | Gratuit | Line item property |
| Lacquering (Yes) | Blades (976), Rubbers (6) | Gratuit | Line item property |
| Gluing (Yes/No) | Rackets (20) | Gratuit | Line item property |
| Option de livraison | Tables (33) | 41–116 € | App tierce |
