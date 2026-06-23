# Guide Projet : Migration Magento vers Shopify (Dandoy-Sports)

Ce fichier centralise le contexte, les contraintes techniques et les directives de développement pour assister l'équipe et les agents IA (Claude Code) dans la migration de l'écosystème Dandoy-Sports & Butterfly.

---

## 1. Contexte & Périmètre du Projet

- **Client :** Dandoy-Sports / Butterfly TT[cite: 1]
- **Objectif :** Migration complète de Magento 1/2 vers Shopify (Instance unique ou multi-boutiques avec Shopify Markets)[cite: 1].
- **Périmètre Multi-sites (6 Domaines/Sous-domaines) :**[cite: 1]
  - `dandoy-sports.com` (Principal)[cite: 1]
  - `fr.dandoy-sports.eu`, `en.dandoy-sports.eu`, `nl.dandoy-sports.eu`[cite: 1]
  - `be.butterfly.tt`, `nl.butterfly.tt` (Identité de marque stricte)[cite: 1]

---

## 2. Contraintes Techniques Majeures (⚠️ À respecter scrupuleusement)

### A. Gestion des Stocks (Pas d'ERP)
- **Fonctionnement :** Une application sur mesure (sans API) génère un export CSV **1x par jour**[cite: 1].
- **Liaison obligatoire :** La synchronisation se fait au caractère près via le **SKU**[cite: 1]. Interdiction stricte de modifier la structure des SKUs existants lors du mapping de données.
- **Outil cible :** Application Shopify *Stock Sync* connectée à un serveur SFTP sécurisé[cite: 1].

### B. Erreur d'Architecture Catalogue (Grouped Products)
- **Le Problème :** Sur Magento, les produits à variantes (ex: une raquette avec plusieurs types de manches) ont été configurés en *Grouped Products* au lieu de Configurable Products[cite: 1].
- **La Solution :** Restructurer la donnée lors de l'import via *Matrixify*. 
  - La colonne Magento `url_key` du produit parent devient le **Handle** unique Shopify.
  - Les lignes enfants (`product_type = simple`) deviennent les **Variantes** Shopify[cite: 1].
  - Les attributs de la colonne `additional_attributes` (ex: `baldes_handles=handle-ANATOMIC`) doivent être convertis en options natives Shopify.

### C. Limites Natives de Shopify
- **Plafond des 100 variantes :** Shopify limite à 100 variantes maximum par fiche produit. Tout groupe Magento dépassant ce seuil (ex: Textiles Taille x Couleur x Coupe) doit être scindé informatiquement en deux fiches distinctes (ex: Modèle Homme / Modèle Femme).

---

## 3. Structure du Dossier de Travail

Le projet est organisé selon l'arborescence suivante. Tout script ou fichier généré doit être classé ici :

```text
📁 MIGRATION_DANDOY_SHOPIFY/
│
├── 📁 01_DATA_RAW/             # Exports bruts CSV/XML de Magento
│   └── 📄 export_magento_products_all.csv
│
├── 📁 02_ANALYSIS_AND_MAPPING/   # Scripts Python/Node, matrices de mapping, audits
│   └── 📄 Intitulés colonnes fichier export
│
├── 📁 03_SEO_AND_REDIRECTS/      # Crawls d'URL et tables de correspondance 301
│
│
└── 📁 04_SHOPIFY_IMPORTS/      # Fichiers nettoyés prêts à l'import (Matrixify)