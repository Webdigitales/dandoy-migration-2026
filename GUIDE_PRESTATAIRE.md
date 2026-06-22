# Guide Prestataire — Synchronisation Stock Dandoy-Sports / Butterfly TT

**Client :** Dandoy-Sports / Butterfly TT
**Contact :** gmonseur@webdigitales.be
**Date :** 22 juin 2026

---

## 1. Contexte

Dandoy-Sports migre de Magento 2 vers Shopify. Il n'y a **pas d'ERP**. La gestion des stocks
repose sur une **application sur mesure** (sans API) qui génère un export CSV des quantités
**une fois par jour**.

Ce document décrit le flux de synchronisation à mettre en place côté Shopify.

---

## 2. Flux actuel (Magento)

```
Application stock (sur mesure)
    │
    ▼  Export CSV 1×/jour
Serveur local / réseau
    │
    ▼  Import automatique
Magento 2 (mise à jour des quantités)
```

L'application n'a pas d'API — la seule interface est le **fichier CSV** qu'elle génère.

---

## 3. Flux cible (Shopify)

```
Application stock (sur mesure)
    │
    ▼  Export CSV 1×/jour
Serveur SFTP sécurisé
    │
    ▼  Lecture automatique (planifiée)
App Shopify "Stock Sync" (ou équivalent)
    │
    ▼  Mise à jour inventaire via Shopify API
Shopify (quantités mises à jour)
```

---

## 4. Contraintes critiques

### 4.1 Liaison par SKU

La correspondance entre le fichier CSV de stock et les produits Shopify se fait
**exclusivement par le SKU** (champ `Variant SKU` dans Shopify).

> **Les SKU ne doivent jamais être modifiés.** La correspondance est au caractère près.
> Tout écart (espace, casse, tiret) empêchera la mise à jour du stock.

### 4.2 Fréquence

L'export CSV est généré **1 fois par jour**. La synchronisation Shopify doit être
planifiée **après** la génération du fichier (vérifier l'heure de génération avec le client).

### 4.3 Pas d'API sur l'application source

L'application de stock n'expose aucune API. Le seul moyen de récupérer les données
est de lire le fichier CSV sur le système de fichiers ou via un transfert SFTP.

---

## 5. Configuration à mettre en place

### 5.1 Serveur SFTP

Mettre en place un serveur SFTP sécurisé accessible par :
- L'application de stock (en écriture) — pour déposer le CSV quotidien
- L'app Shopify Stock Sync (en lecture) — pour récupérer le fichier

**Spécifications :**
- Protocole : SFTP (SSH, port 22)
- Authentification : clé SSH ou identifiants dédiés
- Dossier de dépôt : à convenir (ex: `/stock/`)
- Rétention : conserver les N derniers fichiers pour traçabilité

### 5.2 Format du fichier CSV de stock

Le fichier généré par l'application contient au minimum :

| Colonne | Description | Exemple |
|---|---|---|
| `SKU` | Identifiant produit (= Variant SKU Shopify) | `1033` |
| `QTY` | Quantité en stock | `14` |

> **À vérifier avec le client :** le format exact du CSV (délimiteur, en-têtes,
> colonnes supplémentaires, encodage). Demander un fichier d'exemple.

### 5.3 App Shopify — Stock Sync

**App recommandée :** [Stock Sync](https://apps.shopify.com/stock-sync) par JEXY

Configuration :
- **Source :** SFTP (adresse, port, identifiants, chemin du fichier)
- **Mapping :** colonne SKU → Variant SKU, colonne QTY → Inventory Quantity
- **Planification :** quotidienne, après l'heure de génération du CSV
- **Location :** vérifier que l'inventaire Shopify utilise le bon "location"
  (par défaut : un seul entrepôt)
- **Comportement :** mettre à jour la quantité absolue (pas un delta)

### 5.4 Test de la chaîne

1. Déposer un fichier CSV de test sur le SFTP
2. Déclencher manuellement un sync dans Stock Sync
3. Vérifier dans Shopify Admin → Products qu'un produit a bien sa quantité mise à jour
4. Vérifier avec un SKU connu (ex: SKU `1035` = "Stiga Allround Classic Straight")
5. Planifier le sync automatique

---

## 6. Cas particuliers

### 6.1 Produits à variantes

Un produit Shopify peut avoir plusieurs variantes, chacune avec son propre SKU.
Le fichier CSV de stock contient une ligne par SKU — chaque variante est mise à jour
indépendamment.

Exemple : "Stiga Allround Classic" a 5 variantes (5 SKU distincts : 1033, 1034, 1035, 200, 20).
Chaque SKU a sa propre ligne dans le CSV de stock.

### 6.2 Instance unique vs deux boutiques

Si l'architecture Shopify retenue est l'**instance unique** (recommandé) :
- Un seul flux Stock Sync suffit
- Tous les produits (Dandoy + Butterfly) partagent le même inventaire

Si **deux boutiques** séparées :
- Deux connexions Stock Sync nécessaires (une par boutique)
- Le même fichier CSV peut alimenter les deux (SKU identiques)
- **Risque de survente** sur les 1 386 produits partagés entre les deux boutiques
  (le stock est décrémenté indépendamment, sync seulement 1×/jour)

### 6.3 SKU absents du fichier stock

Définir le comportement quand un SKU Shopify n'est pas présent dans le CSV :
- **Ignorer** (garder la quantité précédente) — recommandé
- **Mettre à zéro** (considérer comme rupture) — risqué si le CSV est partiel

### 6.4 Backorders

Certains produits Magento autorisent les backorders (`allow_backorders=1`).
Dans Shopify, c'est le paramètre "Continue selling when out of stock" sur la variante.
Ce réglage est déjà configuré dans le fichier d'import produits.

---

## 7. Checklist

- [ ] Obtenir un exemple du fichier CSV de stock auprès du client
- [ ] Vérifier le format (délimiteur, en-têtes, encodage, colonnes)
- [ ] Mettre en place le serveur SFTP
- [ ] Configurer l'accès SFTP pour l'application de stock (écriture)
- [ ] Installer et configurer Stock Sync sur Shopify
- [ ] Mapper les colonnes CSV → champs Shopify (SKU, QTY)
- [ ] Tester avec un fichier réel
- [ ] Vérifier la correspondance SKU sur un échantillon
- [ ] Planifier le sync quotidien
- [ ] Documenter l'heure de génération du CSV et l'heure du sync
- [ ] Définir le comportement pour les SKU absents
- [ ] Mettre en place un monitoring (alertes si le sync échoue)
