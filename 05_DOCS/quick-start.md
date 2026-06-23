# Quick Start — Mode d'emploi

Guide pas-à-pas pour importer les données dans Shopify.

---

## Prérequis

- Un compte Shopify avec l'app **Matrixify** installée
- Python 3.12+ (pour régénérer les fichiers si nécessaire)
- L'export Magento dans `01_DATA_RAW/export_magento_products_all.csv`

---

## Étape 1 — Générer les fichiers d'import

```bash
bash 02_ANALYSIS_AND_MAPPING/SCRIPTS/regenerate_all.sh
```

Cela crée dans `04_SHOPIFY_IMPORTS/` :

| Fichier | Contenu |
|---|---|
| `shopify_products.csv` | Produits + variantes + metafields + tags |
| `shopify_translations.csv` | Traductions FR + NL |
| `shopify_collections.csv` | 37 smart collections |
| `shopify_products_PURGE.csv` | Suppression produits (pour tests) |
| `shopify_collections_PURGE.csv` | Suppression collections (pour tests) |
| `shopify_redirects_PURGE.csv` | Suppression redirections (pour tests) |

Et dans `03_SEO_AND_REDIRECTS/` :

| Fichier | Contenu |
|---|---|
| `shopify_redirects.csv` | 2 368 redirections 301 |

---

## Étape 2 — Importer les produits

1. Ouvrir Shopify Admin → **Apps → Matrixify**
2. Cliquer **Import**
3. Uploader `shopify_products.csv`
4. Vérifier le mapping des colonnes (Matrixify les reconnaît automatiquement)
5. Lancer l'import

!!! warning "Images"
    Les URLs images pointent vers `dandoy-sports.com`. Le site Magento doit rester
    en ligne pendant l'import pour que Shopify puisse télécharger les images.

**Vérification :** ouvrir quelques produits dans l'admin et vérifier :

- Titre, description, images
- Variantes (SKU, prix, options)
- Metafields (dans la section "Metafields" de la fiche produit)
- Tags

---

## Étape 3 — Importer les collections

1. Dans Matrixify, cliquer **Import**
2. Uploader `shopify_collections.csv`
3. Lancer l'import

**Vérification :** ouvrir quelques collections et vérifier qu'elles contiennent les bons produits
(le remplissage est automatique via les règles Product Type + Product Tag).

---

## Étape 4 — Activer les langues

1. Aller dans **Settings → Languages**
2. Ajouter **Français (fr)** et **Néerlandais (nl)**
3. Publier les deux langues

---

## Étape 5 — Importer les traductions

1. Dans Matrixify, cliquer **Import**
2. Uploader `shopify_translations.csv`
3. Lancer l'import

**Vérification :** passer la boutique en FR ou NL et vérifier les titres/descriptions traduits.

---

## Étape 6 — Configurer les metafields

Après l'import, Matrixify a créé les définitions automatiquement.
Aller dans **Settings → Custom data → Products** pour :

- Renommer les champs (ex: `custom.blade_category` → "Catégorie bois")
- Ajouter les choix prédéfinis (valeurs listées dans [Metafields](./mapping/metafields.md))

Puis configurer les **filtres** dans **Search & Discovery** :

- Blades : blade_category, blade_feeling
- Rubbers : rubber_category, pimples, hardness
- Clothing/Shoes : gender
- Tables : environment, usage

---

## Étape 7 — Importer les redirections

1. Dans Matrixify, cliquer **Import**
2. Uploader `shopify_redirects.csv` (depuis `03_SEO_AND_REDIRECTS/`)
3. Lancer l'import

**Vérification :** tester quelques anciennes URLs Magento (ex: `/stiga-allround-classic.html`)
pour confirmer la redirection vers `/products/stiga-allround-classic`.

---

## Repartir à zéro (entre les tests)

Pour supprimer toutes les données importées et recommencer :

```
Importer dans cet ordre via Matrixify :
1. shopify_redirects_PURGE.csv
2. shopify_collections_PURGE.csv
3. shopify_products_PURGE.csv
```

> **"Ordre important"**
    Supprimer les redirections et collections **avant** les produits,
    sinon les références seront cassées.

Puis relancer les imports depuis l'étape 2.

---

## Résumé visuel

```
┌─────────────────────────────────────────────────┐
│  regenerate_all.sh                              │
│  (génère tous les CSV depuis l'export Magento)  │
└──────────────────────┬──────────────────────────┘
                       │
        ┌──────────────┼──────────────────┐
        ▼              ▼                  ▼
   Produits      Collections        Redirections
   + Tags        (37 smart)         (2 368 × 301)
   + Metafields
        │              │                  │
        ▼              ▼                  ▼
   Traductions    (auto-remplies)    (après produits)
   FR + NL
        │
        ▼
   Metafields      Search &
   (valider)       Discovery
                   (filtres)
```
