# Plan de migration — Magento → Shopify

---

## Principe clé

Le theming et la configuration se font sur une **boutique Shopify avec de vraies données**
dès la Phase 1. Les scripts permettent de régénérer et réimporter à tout moment via
`Command: MERGE` — les enregistrements existants sont mis à jour sans créer de doublons.

Le **dernier import (J-2 avant go-live)** synchronise les données finales depuis Magento.
Les données de Phase 1 sont intentionnellement "périmées" — elles servent uniquement au theming.

---

## Phase 1 — Foundation (Semaine 1–2)

**Objectif :** boutique Shopify opérationnelle avec catalogue complet.

- Créer boutique Shopify (plan choisi)
- Installer Matrixify Enterprise ($200 — 1 mois)
- Installer apps : Stock Sync, Bold Product Options, Bundles
- Import `shopify_products_sample.csv` → vérifier → supprimer
- Import `shopify_products.csv` (4 834 produits, metafields, tags)
- Import `shopify_collections.csv` (37 collections)
- Configurer metafields — choix prédéfinis
- Configurer Search & Discovery (filtres par collection)
- Activer langues FR + NL dans Settings → Languages
- Import `shopify_translations.csv`

!!! success "Fin de Phase 1"
    Le catalogue complet est visible dans Shopify Admin.
    Le thémiste peut travailler sur de vrais produits.

---

## Phase 2 — Theming & Configuration (Semaine 2–6)

**Objectif :** thème finalisé, apps configurées, parcours client fonctionnel.

- Développement thème Dandoy
- Adaptation branding Butterfly
- Code Liquid — custom options (Gluing, Lacquering, Edge tape)
- Intégration widget Trustpilot (widget Liquid dynamique)
- Configuration Stock Sync + SFTP
- Configuration livraison tables — Bold Product Options (33 produits)
- Migration pages CMS (création manuelle dans Shopify)
- Configuration Shopify Markets (domaines FR/NL/BE/EN)
- Paramétrage taxes, devises, transporteurs

!!! note "Magento continue de tourner"
    La boutique Shopify fonctionne en parallèle. Aucun impact sur les clients.
    Les données peuvent être rafraîchies à tout moment avec `regenerate_all.sh` + réimport MERGE.

---

## Phase 3 — Recette (Semaine 6–7)

**Objectif :** valider l'intégralité du parcours client avant go-live.

| Test | Détail |
|---|---|
| Parcours achat complet (FR / NL / EN) | Paiement test, confirmation, email |
| Custom options | Gluing, Lacquering, Edge tape dans le panier et la commande |
| Livraison tables | Prix variables, options Bold Product Options |
| Filtres par collection | Search & Discovery, toutes langues |
| Affichage metafields sur fiches produit | `technology`, `hardness`, `blade_category`… |
| Widget Trustpilot | SKUs variantes dynamiques |
| Stock Sync | Première synchro SFTP — vérifier niveaux de stock |
| Redirections 301 | Tester 10 URLs Magento → Shopify (HTTP 301) |
| Responsive mobile | Dandoy + Butterfly |
| Email transactionnel | Confirmation commande, expédition, mot de passe |

---

## Phase 4 — Pré-go-live (J-48h)

**Objectif :** données à jour, infrastructure prête pour le switch.

```bash
# Demander le dernier export Magento (produits + clients)
# puis régénérer tous les CSV :
bash 02_ANALYSIS_AND_MAPPING/SCRIPTS/regenerate_all.sh
```

| Tâche | Détail |
|---|---|
| Export Magento final (produits, clients) | Données fraîches J-2 |
| Régénérer CSV (`regenerate_all.sh`) | ~10 min |
| Réimporter produits — MERGE | Met à jour prix, stocks, descriptions |
| Réimporter clients — MERGE | Intègre les nouveaux comptes depuis Phase 1 |
| Import commandes 2025-2026 | `shopify_orders.csv` (37 430 commandes) |
| Import redirections 301 | `shopify_redirects.csv` (2 368) |
| Abaisser le TTL DNS à 300s | Accélère la propagation au go-live |
| Désactiver l'indexation Google sur la boutique Shopify | Évite le doublon SEO avant go-live |
| Brief équipe support | Nouveaux outils, accès Magento en lecture seule disponible |

---

## Phase 5 — Go-live (Jour J)

| Étape | Timing |
|---|---|
| Passer Magento en mode maintenance | 06h00 |
| Dernier export Magento → régénération → réimport MERGE final | 06h00–08h00 |
| Switch DNS | 08h00 |
| Vérifier propagation DNS | 08h00–10h00 |
| Activer redirections Shopify | 08h00 |
| Smoke tests en production (commande test, stock, langues) | 08h00–10h00 |
| Envoyer invitation mot de passe aux clients (email de migration) | J+1 |
| Garder Magento accessible en lecture seule | 6–12 mois |
| Downgrader Matrixify → Basic ($20) ou désinstaller | J+7 |

!!! warning "Fenêtre de maintenance"
    La fenêtre de maintenance Magento (06h00–08h00) est réduite à ~2h grâce à
    `regenerate_all.sh` + Matrixify MERGE. Prévoir un créneau en semaine hors pic de trafic.

---

## Récapitulatif des fichiers d'import

| Ordre | Fichier | Quand |
|---|---|---|
| 1 | `shopify_products_sample.csv` | Phase 1 — test uniquement |
| 2 | `shopify_products.csv` | Phase 1 |
| 3 | `shopify_collections.csv` | Phase 1 |
| 4 | `shopify_translations.csv` | Phase 1 |
| 5 | `shopify_customers.csv` | Phase 4 (J-2) |
| 6 | `shopify_orders.csv` | Phase 4 (J-2) |
| 7 | `shopify_redirects.csv` | Phase 4 (J-2) |

Les fichiers 2–4 peuvent être réimportés autant de fois que nécessaire (MERGE).
Les fichiers 5–7 sont importés une seule fois, au plus proche du go-live.

---

## Décisions en attente avant de démarrer

| Sujet | Impact |
|---|---|
| **Multi-sites** : instance unique (recommandé) ou deux boutiques ? | Conditionne la configuration Markets et les domaines |
| **Plan Shopify** : Basic / Shopify / Advanced / Plus ? | Conditionne les frais de transaction et les fonctionnalités Markets |
| **Thème** : thème premium du marché ou développement sur mesure ? | Conditionne le planning Phase 2 |
