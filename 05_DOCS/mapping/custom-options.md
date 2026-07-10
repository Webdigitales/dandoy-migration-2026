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
| **Gluing** | Radio | Non | Yes, No | Gratuit | 39 produits |

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

#### Le `product.type` seul ne suffit pas

Une logique conditionnelle basée uniquement sur `product.type` (`Rubbers`, `Blades`, `Rackets`)
suraffiche largement les sélecteurs : l'analyse produit par produit (hors doublons multi-langues,
sur `export_magento_products_all.csv`) montre un écart important au cas général au sein d'un
même type :

| Type | Combinaison dominante | Écart au cas général |
|---|---|---|
| Rubbers (4 790 produits) | Gluing seul (78,9 %) | **749 produits (15,6 %)** sans aucune option, 251 (5,2 %) avec Edge tape en plus |
| Blades (2 791 produits) | Lacquering (72,3 %) | **774 produits (27,7 %)** sans aucune option |
| Rackets (170 produits) | Aucune option (77,1 %) | 39 produits (22,9 %) avec Gluing |

Avec un simple `{% if product.type == 'Rubbers' %}`, environ 750 produits Rubbers et 775 Blades
afficheraient un sélecteur qui ne s'applique pas à eux (un client pourrait choisir "Gluing:
Forehand" sur un produit où cette préférence n'a aucun sens côté atelier).

#### Solution retenue : metafield par produit, alimenté à l'import

`magento_to_shopify.py` extrait désormais la colonne source `custom_options` (déjà présente dans
l'export Magento) et la normalise dans le metafield **`custom.available_options`**
(`list.single_line_text_field`, séparateur `;`), avec les valeurs possibles `Gluing`, `EdgeTape`,
`Lacquering`. Pour les produits *grouped* (voir section 2.B du guide projet), les `custom_options`
sont portées par les **SKUs enfants simples**, pas par le parent — le script fait l'union des
options de tous les enfants pour peupler le metafield du produit Shopify.

Le thème lit ce metafield au lieu de coder en dur une condition par `product.type` :

```liquid
{% assign opts = product.metafields.custom.available_options.value %}

{% if opts contains 'Gluing' %}
  <div class="product-option">
    <label for="gluing">Gluing</label>
    <select name="properties[Gluing]" id="gluing">
      <option value="">— None —</option>
      <option value="Forehand">Forehand</option>
      <option value="Backhand">Backhand</option>
    </select>
  </div>
{% endif %}

{% if opts contains 'EdgeTape' %}
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

{% if opts contains 'Lacquering' %}
  <div class="product-option">
    <label>
      <input type="checkbox" name="properties[Lacquering]" value="Yes">
      Lacquering
    </label>
  </div>
{% endif %}
```

Les valeurs possibles par option (Forehand/Backhand, Dandoy/Donic/Stiga…) restent codées dans le
thème — elles sont stables et communes à tous les produits concernés, un metafield dédié par
valeur n'apporterait rien de plus.

#### Intégration dans le thème Horizon

Horizon (thème par défaut Shopify 2025+) n'a pas de `sections/main-product.liquid` monolithique
comme Dawn : la page produit (`sections/product-information.liquid`) délègue tout à des
**theme blocks**. Le code ci-dessus doit donc être packagé en tant que nouveau block plutôt
qu'injecté directement dans une section.

1. **Créer le fichier de block**, par ex. `blocks/custom-options.liquid`, avec le Liquid
   ci-dessus suivi d'un schema minimal (pas de réglage marchand nécessaire, tout vient du
   metafield) :

   ```liquid
   {% schema %}
   {
     "name": "Custom options",
     "settings": []
   }
   {% endschema %}
   ```

   ⚠️ `"target"` n'est **pas** une clé valide du schema d'un block (contrairement à ce que
   suggèrent certains articles tiers) — seule la section qui accueille le block doit déclarer
   `"blocks": [{ "type": "@theme" }, { "type": "@app" }]`, ce que `product-information.liquid`
   fait déjà nativement.

2. **Enregistrer le block dans `templates/product.json`**, à l'intérieur de
   `sections.main.blocks["product-details"]` (pas au niveau racine de la section), et
   l'insérer dans le `block_order` de ce même `product-details`, juste avant `buy_buttons_*`
   pour qu'il reste dans le même formulaire produit que le bouton d'achat :

   ```json
   "custom_options_1": {
     "type": "custom-options",
     "settings": {},
     "blocks": {}
   }
   ```

   avec `custom_options_1` ajouté au `block_order` juste avant l'entrée `buy_buttons_*`.

   Le plus sûr reste d'ajouter le block **via l'éditeur de thème** (Personnaliser → section
   produit → bloc "Product details" → Ajouter un bloc) plutôt que d'éditer `product.json` à la
   main : ce fichier est auto-généré et un futur enregistrement depuis l'éditeur peut écraser
   une modification manuelle.

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

Occurrences côté source Magento (SKU simples, avant regroupement en produits Shopify) :

| Option | Produits | Prix | Solution Shopify |
|---|---|---|---|
| Gluing (Forehand/Backhand) | Rubbers (4 009), Rackets (39) | Gratuit | Line item property |
| Edge tape (Dandoy/Donic/Stiga) | Rubbers (342) | Gratuit | Line item property |
| Lacquering (Yes) | Blades (976), Rubbers (6) | Gratuit | Line item property |
| Option de livraison | Tables (33) | 41–116 € | App tierce |

Résultat après regroupement en produits Shopify (`shopify_products.csv`, metafield
`custom.available_options`) :

| Option | Produits Shopify concernés |
|---|---|
| Gluing | 723 |
| Lacquering | 735 |
| EdgeTape | 57 |

> Le nombre de produits Shopify est très inférieur au nombre de SKUs Magento car plusieurs SKUs
> (couleurs, épaisseurs) sont regroupés en un seul produit Shopify avec variantes — voir section
> 2.B du guide projet.
