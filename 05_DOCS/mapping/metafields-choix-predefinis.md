# Metafields — Choix prédéfinis

Valeurs à configurer dans Shopify Admin après l'import Matrixify pour éviter
les erreurs de saisie lors de l'ajout de nouveaux produits.

**Chemin :** Settings → Custom data → Products → *(cliquer sur la définition)* → Validation → Predefined choices

---

## `custom.promotion` — Promotion

```
2 = 3, 3 = 4, Liquidation, NEW, promo, solde
```

## `custom.blade_category` — Catégorie bois

```
ALL, ALL+, ALL-, DEF, DEF+, OFF, OFF+, OFF-
```

## `custom.blade_layers` — Nombre de plis

```
1, 3, 3+2, 4, 4+1, 5, 5+2, 5+4, 6, 6+2, 7, 7+2, 7+6, 9, 11, 17
```

## `custom.blade_feeling` — Sensation

```
hard, medium, soft
```

## `custom.rubber_category` — Catégorie revêtement

```
ALL, ALL+, ALL-, DEF, DEF+, OFF, OFF+, OFF-
```

## `custom.pimples` — Type de picots

```
Anti, Long pimple, Pimple in, Short pimple
```

## `custom.hardness` — Dureté

```
Hard, Medium, Soft
```

## `custom.shoe_type` — Type de chaussure

```
Exterior, Interior
```

## `custom.bag_model` — Modèle de sac

```
AluCase, backpack, BatcoverSimple, BatwalletDouble, BatwalletSimple, Sportbag, Trolleybag
```

## `custom.ball_usage` — Usage balle

```
Competition, Fun, Training
```

## `custom.ball_material` — Matériau balle

```
Celluloid, Plastic
```

## `custom.usage` — Usage

```
Leisure, Pro
```

## `custom.accessory_type` — Type d'accessoire

```
Arbitration Kits, Caps, Edge Tape, Fun Balls, Glue, Headbands, Keychains, Overgrips, Protectors Sheets, Sponge, Towel, Water Bottle, Wristbands
```

## `custom.environment` — Environnement

```
Indoor, Outdoor
```

## `custom.gender` — Genre

```
Child, Man, Unisex, Woman
```

---

## Metafields sans choix prédéfinis

| Metafield | Raison |
|---|---|
| `custom.technology` | 77 valeurs par marque — affichage fiche produit uniquement, texte libre |
| `custom.dimension` | Dimensions libres (49 valeurs différentes) |
| `custom.video_url` | URLs YouTube |
| `custom.cover_included` | Boolean (true/false, pas de choix à configurer) |
