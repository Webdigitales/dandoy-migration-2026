# Quick Start — Mode d'emploi

Guide pas-à-pas pour importer les données dans Shopify.

> **Deux boutiques Shopify (Option B)** : Dandoy-Sports et Butterfly TT sont deux instances
> séparées. Chaque étape ci-dessous s'exécute **deux fois**, une fois par boutique, avec le
> fichier `_dandoy` ou `_butterfly` correspondant. Voir [Multi-sites](./architecture/multi-sites.md).

---

## Prérequis

- Un compte Shopify (× 2 : Dandoy-Sports + Butterfly TT) avec l'app **Matrixify** installée sur chacun
- Python 3.12+ (pour régénérer les fichiers si nécessaire)
- L'export Magento dans `01_DATA_RAW/export_magento_products_all.csv`

---

## Étape 1 — Générer les fichiers d'import

```bash
bash 02_ANALYSIS_AND_MAPPING/SCRIPTS/regenerate_all.sh
```

Cela crée dans `04_SHOPIFY_IMPORTS/`, un jeu de fichiers par boutique :

| Fichier | Contenu |
|---|---|
| `shopify_products_dandoy.csv` / `shopify_products_butterfly.csv` | Produits + variantes + metafields + tags |
| `shopify_translations_dandoy.csv` / `shopify_translations_butterfly.csv` | Traductions FR + NL |
| `shopify_collections_dandoy.csv` / `shopify_collections_butterfly.csv` | 37 smart collections |
| `shopify_customers_dandoy.csv` / `shopify_customers_butterfly.csv` | Clients dédupliqués |
| `shopify_orders_dandoy.csv` / `shopify_orders_butterfly.csv` | Commandes 2025-2026 |
| `shopify_products_{dandoy\|butterfly}_PURGE.csv` | Suppression produits (pour tests) |
| `shopify_collections_{dandoy\|butterfly}_PURGE.csv` | Suppression collections (pour tests) |
| `shopify_redirects_{dandoy\|butterfly}_PURGE.csv` | Suppression redirections (pour tests) |
| `shopify_orders_{dandoy\|butterfly}_PURGE.csv` | Suppression commandes (pour tests) |

Et dans `03_SEO_AND_REDIRECTS/` :

| Fichier | Contenu |
|---|---|
| `shopify_redirects_dandoy.csv` | 2 045 redirections 301 |
| `shopify_redirects_butterfly.csv` | 380 redirections 301 |

> Les **199 produits partagés** entre Dandoy et Butterfly (35 actifs) sont présents dans les
> deux fichiers produits, tagués `dandoy,butterfly` — aucune étape manuelle supplémentaire,
> importer normalement dans chaque boutique.

---

## Étape 2 — Tester avec le sample

Avant d'importer le catalogue complet, vérifier le format avec l'échantillon **dans chaque
boutique** :

1. Ouvrir Shopify Admin (boutique Dandoy ou Butterfly) → **Apps → Matrixify**
2. Cliquer **Import**
3. Uploader `shopify_products_sample_dandoy.csv` (ou `_butterfly.csv` selon la boutique — tous types représentés)
4. Lancer l'import
5. Vérifier dans l'admin : variantes, metafields, tags, images

Si tout est OK, purger le sample (`shopify_products_{store}_PURGE.csv` ou suppression manuelle)
puis passer à l'étape 3.

---

## Étape 3 — Importer les produits

1. Dans Matrixify, cliquer **Import**
2. Uploader `shopify_products_dandoy.csv` (boutique Dandoy) ou `shopify_products_butterfly.csv` (boutique Butterfly)
3. Vérifier le mapping des colonnes (Matrixify les reconnaît automatiquement)
4. Lancer l'import

!!! warning "Images"
    Les URLs images pointent vers `dandoy-sports.com`. Le site Magento doit rester
    en ligne pendant l'import pour que Shopify puisse télécharger les images.

**Vérification :** ouvrir quelques produits dans l'admin et vérifier :

- Titre, description, images
- Variantes (SKU, prix, options)
- Metafields (dans la section "Metafields" de la fiche produit)
- Tags (dont `dandoy` / `butterfly`, et les deux sur les produits partagés)

---

## Étape 4 — Importer les collections

1. Dans Matrixify, cliquer **Import**
2. Uploader `shopify_collections_dandoy.csv` ou `shopify_collections_butterfly.csv`
3. Lancer l'import

**Vérification :** ouvrir quelques collections et vérifier qu'elles contiennent les bons produits
(le remplissage est automatique via les règles Product Type + Product Tag, évaluées sur le
catalogue propre à chaque boutique).

---

## Étape 5 — Activer les langues

1. Aller dans **Settings → Languages**
2. Boutique Dandoy : ajouter **Français (fr)**, **Anglais (en)** et **Néerlandais (nl)**
3. Boutique Butterfly : ajouter **Français (fr)** et **Néerlandais (nl)**
4. Publier les langues

---

## Étape 6 — Importer les traductions

1. Dans Matrixify, cliquer **Import**
2. Uploader `shopify_translations_dandoy.csv` ou `shopify_translations_butterfly.csv`
3. Lancer l'import

**Vérification :** passer la boutique en FR ou NL et vérifier les titres/descriptions traduits.

---

## Étape 7 — Configurer les metafields

Après l'import, Matrixify a créé les définitions automatiquement (à faire dans **chaque**
boutique). Aller dans **Settings → Custom data → Products** pour :

- Renommer les champs (ex: `custom.blade_category` → "Catégorie bois")
- Ajouter les choix prédéfinis (valeurs listées dans [Metafields — Choix prédéfinis](./mapping/metafields-choix-predefinis.md))

Puis configurer les **filtres** dans **Search & Discovery** :

- Blades : blade_category, blade_feeling
- Rubbers : rubber_category, pimples, hardness
- Clothing/Shoes : gender
- Tables : environment, usage

---

## Étape 8 — Importer les redirections

1. Dans Matrixify, cliquer **Import**
2. Uploader `shopify_redirects_dandoy.csv` ou `shopify_redirects_butterfly.csv` (depuis `03_SEO_AND_REDIRECTS/`)
3. Lancer l'import

**Vérification :** tester quelques anciennes URLs Magento (ex: `/stiga-allround-classic.html`)
pour confirmer la redirection vers `/products/stiga-allround-classic` sur la bonne boutique.

---

## Repartir à zéro (entre les tests)

Pour supprimer toutes les données importées d'une boutique et recommencer :

```
Importer dans cet ordre via Matrixify (fichiers _dandoy ou _butterfly selon la boutique) :
1. shopify_orders_{store}_PURGE.csv
2. shopify_redirects_{store}_PURGE.csv
3. shopify_collections_{store}_PURGE.csv
4. shopify_products_{store}_PURGE.csv
```

> **Ordre important**
    Supprimer les redirections et collections **avant** les produits,
    sinon les références seront cassées.

Puis relancer les imports depuis l'étape 2, dans la boutique concernée.

---

## Résumé visuel

```
┌─────────────────────────────────────────────────┐
│  regenerate_all.sh                              │
│  (génère les CSV des 2 boutiques depuis         │
│   l'export Magento)                             │
└──────────────────────┬──────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        ▼                              ▼
   Boutique Dandoy-Sports        Boutique Butterfly TT
        │                              │
        ├─ Produits + Tags + Metafields ┤
        ├─ Collections (37 smart)       ┤
        ├─ Langues (FR/EN/NL vs FR/NL)  ┤
        ├─ Traductions                  ┤
        └─ Redirections (2 045 / 380)   ┘
```
