# Plan de migration — Magento → Shopify

---

## Principe clé

**Deux boutiques Shopify séparées** (Option B, décidée le 29 juillet 2026) : Dandoy-Sports
(plan complet) et Butterfly TT (plan Basic). Chaque phase ci-dessous s'exécute dans les deux
boutiques, sauf mention contraire — voir [Multi-sites](../architecture/multi-sites.md).

Le theming et la configuration se font sur des **boutiques Shopify avec de vraies données**
dès la Phase 1. Les scripts permettent de régénérer et réimporter à tout moment via
`Command: MERGE` — les enregistrements existants sont mis à jour sans créer de doublons.

Le **dernier import (J-2 avant go-live)** synchronise les données finales depuis Magento.
Les données de Phase 1 sont intentionnellement "périmées" — elles servent uniquement au theming.

---

## Phase 1 — Foundation

**Objectif :** les deux boutiques Shopify opérationnelles avec leur catalogue complet.

- Créer les deux boutiques Shopify (Dandoy-Sports plan complet, Butterfly TT plan Basic)
- Installer Matrixify Enterprise ($200 — 1 mois) sur les deux boutiques
- Installer apps : Stock Sync, Bold Product Options, Bundles (sur chaque boutique concernée)
- Import `shopify_products_sample_{dandoy|butterfly}.csv` → vérifier → supprimer
- Import `shopify_products_{dandoy|butterfly}.csv` (4 183 / 849 produits, metafields, tags —
  199 produits partagés dupliqués dans les deux)
- Import `shopify_collections_{dandoy|butterfly}.csv` (37 collections, dans chaque boutique)
- Configurer metafields — choix prédéfinis (dans chaque boutique)
- Configurer Search & Discovery (filtres par collection, dans chaque boutique)
- Activer langues dans Settings → Languages : FR + EN + NL (Dandoy), FR + NL (Butterfly)
- Import `shopify_translations_{dandoy|butterfly}.csv`

!!! success "Fin de Phase 1"
    Le catalogue complet est visible dans les deux boutiques Shopify Admin.
    Le thémiste peut travailler sur de vrais produits.

---

## Phase 2 — Theming & Configuration

**Objectif :** deux thèmes finalisés (un par boutique), apps configurées, parcours client fonctionnel.

- Développement thème Dandoy (boutique Dandoy-Sports)
- Développement thème Butterfly — branding 100% dédié (boutique Butterfly TT, plan Basic)
- Code Liquid — custom options (Gluing, Lacquering, Edge tape), sur les deux thèmes
- Intégration widget Trustpilot (widget Liquid dynamique), sur les deux thèmes
- Configuration Stock Sync + SFTP — **deux connexions**, même fichier CSV de stock (SKU identiques)
- Configuration livraison tables — Bold Product Options (33 produits, boutique Dandoy)
- Migration pages CMS (création manuelle dans Shopify, sur chaque boutique)
- Configuration Shopify Markets **côté Dandoy uniquement** (hors-UE `.com` vs UE `.eu` —
  Butterfly n'a pas besoin de Markets, ses deux domaines BE/NL sont sur la même zone tarifaire)
- Paramétrage taxes, devises, transporteurs (par boutique)
- Vérifier les limitations du plan Basic (Butterfly) : rapports, shipping tiers calculé, comptes staff

!!! note "Magento continue de tourner"
    Les boutiques Shopify fonctionnent en parallèle. Aucun impact sur les clients.
    Les données peuvent être rafraîchies à tout moment avec `regenerate_all.sh` + réimport MERGE.

---

## Phase 3 — Recette

**Objectif :** valider l'intégralité du parcours client avant go-live.

| Test | Détail |
|---|---|
| Parcours achat complet — Dandoy (FR / EN / NL) | Paiement test, confirmation, email |
| Parcours achat complet — Butterfly (FR / NL) | Paiement test, confirmation, email |
| Custom options | Gluing, Lacquering, Edge tape dans le panier et la commande (les deux boutiques) |
| Livraison tables | Prix variables, options Bold Product Options (boutique Dandoy) |
| Filtres par collection | Search & Discovery, toutes langues, les deux boutiques |
| Affichage metafields sur fiches produit | `technology`, `hardness`, `blade_category`… (les deux boutiques) |
| Widget Trustpilot | SKUs variantes dynamiques (les deux boutiques) |
| Stock Sync | Deux synchros SFTP (une par boutique) — vérifier niveaux de stock, y compris produits partagés |
| Redirections 301 | Tester 10 URLs Magento → Shopify (HTTP 301), sur chaque domaine |
| Responsive mobile | Dandoy + Butterfly |
| Email transactionnel | Confirmation commande, expédition, mot de passe (les deux boutiques) |
| Plan Basic Butterfly | Vérifier que les fonctionnalités nécessaires sont bien disponibles |

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
| Régénérer CSV (`regenerate_all.sh`) | ~10 min, génère les fichiers des 2 boutiques |
| Réimporter produits — MERGE | Dans chaque boutique — met à jour prix, stocks, descriptions |
| Réimporter clients — MERGE | Dans chaque boutique — intègre les nouveaux comptes depuis Phase 1 |
| Import commandes 2025-2026 | `shopify_orders_dandoy.csv` (23 823) / `shopify_orders_butterfly.csv` (13 607) |
| Import redirections 301 | `shopify_redirects_dandoy.csv` (2 045) / `shopify_redirects_butterfly.csv` (380) |
| Abaisser le TTL DNS à 300s | Sur les 6 domaines, accélère la propagation au go-live |
| Désactiver l'indexation Google sur les boutiques Shopify | Évite le doublon SEO avant go-live |
| Brief équipe support | Nouveaux outils, accès Magento en lecture seule disponible |

---

## Phase 5 — Go-live (Jour J)

| Étape | Timing |
|---|---|
| Passer Magento en mode maintenance | 06h00 |
| Dernier export Magento → régénération → réimport MERGE final (2 boutiques) | 06h00–08h00 |
| Switch DNS (6 domaines, vers les 2 boutiques) | 08h00 |
| Vérifier propagation DNS | 08h00–10h00 |
| Activer redirections Shopify (2 boutiques) | 08h00 |
| Smoke tests en production (commande test, stock, langues, sur les 2 boutiques) | 08h00–10h00 |
| Envoyer invitation mot de passe aux clients (email de migration) | J+1 |
| Garder Magento accessible en lecture seule | 6–12 mois |
| Downgrader Matrixify → Basic ($20) ou désinstaller (sur les 2 boutiques) | J+7 |

!!! warning "Fenêtre de maintenance"
    La fenêtre de maintenance Magento (06h00–08h00) est réduite à ~2h grâce à
    `regenerate_all.sh` + Matrixify MERGE. Prévoir un créneau en semaine hors pic de trafic.

---

## Récapitulatif des fichiers d'import

Chaque fichier existe en deux versions (`_dandoy` / `_butterfly`), importées séparément dans
leur boutique respective.

| Ordre | Fichier | Quand |
|---|---|---|
| 1 | `shopify_products_sample_{store}.csv` | Phase 1 — test uniquement |
| 2 | `shopify_products_{store}.csv` | Phase 1 |
| 3 | `shopify_collections_{store}.csv` | Phase 1 |
| 4 | `shopify_translations_{store}.csv` | Phase 1 |
| 5 | `shopify_customers_{store}.csv` | Phase 4 (J-2) |
| 6 | `shopify_orders_{store}.csv` | Phase 4 (J-2) |
| 7 | `shopify_redirects_{store}.csv` | Phase 4 (J-2) |

Les fichiers 2–4 peuvent être réimportés autant de fois que nécessaire (MERGE).
Les fichiers 5–7 sont importés une seule fois, au plus proche du go-live.

---

## Décisions en attente avant de démarrer

| Sujet | Statut |
|---|---|
| **Multi-sites** : instance unique ou deux boutiques ? | **Tranché** — Option B (deux boutiques séparées), décidé le 29 juillet 2026 |
| **Plan Shopify** : Basic / Shopify / Advanced / Plus ? | **Tranché** — Dandoy-Sports plan complet, Butterfly TT plan Basic |
| **Limitations du plan Basic (Butterfly)** | À vérifier avant validation finale (rapports pro, shipping tiers calculé, comptes staff) |
| **Thème** : thème premium du marché ou développement sur mesure ? | À décider — conditionne le planning Phase 2 (× 2 thèmes à prévoir) |
