# Guide Prestataire — Migration Shopify Dandoy-Sports / Butterfly TT

**Client :** Dandoy-Sports / Butterfly TT
**Contact :** gmonseur@webdigitales.be
**Date :** 22 juin 2026

---

## 1. Contexte

Migration complète d'un écosystème Magento 2 (6 domaines, 3 langues) vers Shopify.

### Domaines à couvrir

| Domaine | Usage |
|---|---|
| `dandoy-sports.com` | Boutique principale |
| `fr.dandoy-sports.eu` | Dandoy francophone |
| `en.dandoy-sports.eu` | Dandoy anglophone |
| `nl.dandoy-sports.eu` | Dandoy néerlandophone |
| `be.butterfly.tt` | Butterfly Belgique (marque distincte) |
| `nl.butterfly.tt` | Butterfly Pays-Bas |

### Langues

- **Anglais** : langue par défaut (contenu principal du catalogue)
- **Français** : 93% des produits traduits
- **Néerlandais** : 71% des produits traduits

---

## 2. Ce qui est prêt (fichiers d'import)

Tous les fichiers sont au **format Matrixify** et prêts à l'import.

| Fichier | Contenu | Lignes |
|---|---|---|
| `shopify_products.csv` | 4 834 produits + 19 metafields + tags | 25 514 |
| `shopify_translations.csv` | Traductions FR + NL | 6 723 |
| `shopify_collections.csv` | 37 smart collections (16 top-level + 21 sous-catégories) | 58 |
| `shopify_redirects.csv` | Redirections 301 | 2 368 |
| `shopify_products_sample.csv` | Échantillon 10 produits pour test | 53 |

### Ordre d'import

1. **Produits** (`shopify_products.csv`)
2. **Collections** (`shopify_collections.csv`) — se remplissent automatiquement via les tags/types
3. Activer les langues FR et NL dans **Settings → Languages**
4. **Traductions** (`shopify_translations.csv`)
5. **Redirections** (`shopify_redirects.csv`) — après vérification que les URLs cibles existent

---

## 3. Décisions à prendre avec le client

### 3.1 Architecture multi-sites

Deux options analysées (voir `multi_sites_shopify.md` pour le détail) :

| | Option A — Instance unique + Markets | Option B — Deux boutiques |
|---|---|---|
| Principe | Un seul catalogue, Shopify Markets pour les domaines | Dandoy et Butterfly séparés |
| Stock | Unifié, pas de risque de survente | Dupliqué, risque de survente (sync 1×/jour) |
| Produits partagés (1 386) | Gérés nativement | Dupliqués manuellement |
| Coût | 1 abonnement | 2 abonnements |
| Branding Butterfly | Thème adaptatif / sections conditionnelles | Thème 100% dédié |
| **Recommandation** | **Oui** | Non (sauf exigence branding strict) |

> **Impact :** cette décision conditionne la configuration des domaines, les thèmes,
> et le flux Stock Sync. À trancher en priorité.

### 3.2 Custom options produits

Certains produits Magento ont des options de personnalisation (pas des variantes) :

| Option | Produits | Solution recommandée |
|---|---|---|
| **Gluing** (Forehand/Backhand) | 4 009 revêtements | Line item property (code thème Liquid) |
| **Edge tape** (Dandoy/Donic/Stiga) | 342 revêtements | Line item property |
| **Lacquering** (checkbox) | 976 bois | Line item property |
| **Option de livraison tables** | 33 tables | App tierce (impact prix 41–116 €) |

Voir `custom_options_shopify.md` pour le code Liquid et les détails.

### 3.3 Bundles (promotions "3=4")

105 bundles Magento dont 21 actifs (principalement des promos "achetez 3, recevez 4").
Pas de migration data nécessaire — les produits composants sont déjà dans l'export.

| Solution | Usage |
|---|---|
| **Remise automatique** Shopify (Buy 3 Get 1 Free) | 17 promos "3=4" rubbers |
| **Shopify Bundles app** (gratuit) | 4 bundles divers |

Voir `bundles_shopify.md` pour la liste complète.

---

## 4. Points techniques

### 4.1 Variantes produits

Les produits Magento étaient en "Grouped Products" (et non Configurable). La restructuration
est faite dans le CSV : chaque enfant simple devient une variante Shopify.

Options mappées par type :

| Type | Option1 | Option2 |
|---|---|---|
| Blades (bois) | Handle (Anatomic, Flared…) | — |
| Rubbers (revêtements) | Color (Red, Black…) | Thickness (1.7, 1.9…) |
| Clothing (textiles) | Size (XS→5XL) | — |
| Shoes (chaussures) | Size (36→46) | — |
| Bags (sacs) | Color | — |
| Balls (balles) | Quantity (3, 12, 72…) | Color |
| Cleaners (nettoyants) | Quantity (100ml, 250ml…) | — |

Max de variantes constaté : **33** (bien sous la limite Shopify de 100).

### 4.2 Metafields (19 champs custom)

Matrixify crée automatiquement les définitions à l'import.
**Après l'import, valider dans Settings → Custom data → Products :**
- Vérifier les noms affichés
- Configurer les choix prédéfinis (valeurs listées dans `metafields_shopify.md`)

Metafields recommandés comme **filtres** dans Search & Discovery :
- Blades : `custom.blade_category`, `custom.blade_feeling`
- Rubbers : `custom.rubber_category`, `custom.pimples`, `custom.hardness`
- Clothing/Shoes : `custom.gender`
- Tables : `custom.environment`, `custom.usage`
- Tous : `custom.promotion`

> **Note :** les options de variantes (Color, Size, Handle…) sont filtrables nativement
> dans Search & Discovery — pas besoin de les dupliquer en metafields.

### 4.3 Images

Les URLs images pointent vers `https://www.dandoy-sports.com/pub/media/catalog/product/…`.
Shopify les téléchargera au moment de l'import Matrixify.

**Le site Magento doit rester en ligne** pendant l'import des produits.

### 4.4 Stock

- Pas d'ERP — une application sur mesure génère un CSV de stock **1×/jour**
- La liaison se fait via le **SKU** (correspondance au caractère près)
- Outil cible : **Stock Sync** connecté à un serveur **SFTP**
- **Ne pas modifier les SKU** lors de la migration

### 4.5 Redirections 301

2 368 redirections générées (uniquement les URLs actives, vérifiées par test HTTP).
Format : `/{url_key}.html` → `/products/{handle}`

Import via Matrixify dans le fichier Redirects (après l'import produits).

### 4.6 Store views obsolètes

Deux store views Magento sont à **exclure** de la migration :
- `eu_en_old` — ancienne vue anglaise Dandoy, remplacée par `eu_en`
- `bt_be_en` — vue anglaise Butterfly, non utilisée

---

## 5. Documentation de référence

Toute la documentation détaillée est dans le dossier `02_ANALYSIS_AND_MAPPING/` :

| Document | Contenu |
|---|---|
| `matrice_data_mapping_products.md` | Mapping colonnes Magento → Shopify |
| `metafields_shopify.md` | 19 metafields : définitions, types, valeurs, filtrage |
| `custom_options_shopify.md` | Options custom → line item properties (code Liquid inclus) |
| `gestion_langues_shopify.md` | Stratégie traductions FR/NL, workflow Matrixify |
| `multi_sites_shopify.md` | Comparatif instance unique vs deux boutiques |
| `regles_import_matrixify.md` | Règles d'import Matrixify (format, commandes, limites) |
| `redirections_301.md` | Stratégie redirections SEO |
| `bundles_shopify.md` | Stratégie bundles (remises auto, pas de migration data) |
| `avancement_migration.md` | État d'avancement complet et historique |

---

## 6. Reste à faire (prestataire)

| Tâche | Priorité | Dépendance |
|---|---|---|
| Valider le choix multi-sites avec le client | **Haute** | — |
| Configurer Shopify (boutique, domaines, langues, Markets) | **Haute** | Décision multi-sites |
| Importer les fichiers CSV via Matrixify | **Haute** | Config Shopify |
| Configurer les metafields (noms, choix prédéfinis) | Haute | Après import produits |
| Configurer Search & Discovery (filtres) | Haute | Après metafields |
| Thème Shopify + intégration line item properties | Haute | — |
| Configurer Stock Sync (SFTP) | **Haute** | Serveur SFTP fourni par le client |
| Créer les remises automatiques (bundles 3=4) | Moyenne | Après import produits |
| Configurer l'app livraison tables (33 produits) | Basse | Choix de l'app |
| Migration clients / commandes (si souhaité) | À évaluer | Décision client |
| Pages CMS | Basse | — |
| Crawl post-migration (404, SEO) | Moyenne | Après mise en ligne |

---

## 7. Scripts (régénération des fichiers)

Les fichiers d'import sont générés par des scripts Python dans `02_ANALYSIS_AND_MAPPING/SCRIPTS/`.
En cas de mise à jour de l'export Magento, il suffit de relancer :

```bash
# Produits + traductions
python3 02_ANALYSIS_AND_MAPPING/SCRIPTS/magento_to_shopify.py

# Collections
python3 02_ANALYSIS_AND_MAPPING/SCRIPTS/generate_collections.py

# Redirections
python3 02_ANALYSIS_AND_MAPPING/SCRIPTS/generate_redirects.py
```

Source : `01_DATA_RAW/export_magento_products_all.csv` (export Magento du 12 juin 2026).
