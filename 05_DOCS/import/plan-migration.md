# Plan de migration — Magento → Shopify

---

## Principe clé

**Deux boutiques Shopify séparées** (Option B, décidée le 29 juillet 2026) : Dandoy-Sports
(**Shopify Plus**) et Butterfly TT (plan Basic). Chaque phase ci-dessous s'exécute dans les deux
boutiques, sauf mention contraire — voir [Multi-sites](../architecture/multi-sites.md).

Le plan Plus de Dandoy-Sports rend le **B2B natif (Companies)** disponible pour gérer les clubs
partenaires — voir [Remises club & B2B](../mapping/club-b2b.md).

Le theming et la configuration se font sur des **boutiques Shopify avec de vraies données**
dès la Phase 1. Les scripts permettent de régénérer et réimporter à tout moment via
`Command: MERGE` — les enregistrements existants sont mis à jour sans créer de doublons.
**Tous les fichiers du pipeline sont en `MERGE`** (produits, collections, redirections,
clients, commandes, companies) : un réimport complet ultérieur ne crée jamais de doublon.

Le **dernier import (J-2 avant go-live)** synchronise les données finales depuis Magento.
Les données de Phase 1 sont intentionnellement "périmées" — elles servent uniquement au theming.

### Stratégie en 2 passes pour les entités sensibles au temps (décidée le 20 août 2026)

Clients, commandes et Companies peuvent être importés en réel **bien avant le go-live** (une
1ère synchro complète, données arrêtées à une date donnée) puis **resynchronisés à neuf juste
avant le go-live** — sûr grâce à `MERGE`, aucun calcul de delta à faire à la main :

1. **1ère synchro complète** — clients + commandes + companies dans leur état à une date T
   (ex. 20 août 2026). Companies : pas de risque tant qu'aucun nouveau club n'a été créé côté
   Magento entre-temps (un client rejoignant un club déjà existant est un risque mineur accepté,
   couvert de toute façon par la resynchro finale).
2. **Migration définitive (J-2 / go-live)** — régénérer **tout** (`regenerate_all.sh`) depuis un
   export Magento frais et réimporter (MERGE) : nouveaux clients, nouvelles commandes, nouvelles
   adhésions club depuis T sont intégrés automatiquement.

**Les chèques cadeaux suivent une logique à part** (pas de `Command: MERGE` — c'est un appel API
direct, pas un import CSV, et une carte cadeau créée deux fois avec le même code échoue plutôt
que de fusionner) : un échantillon réduit est migré dès maintenant pour valider le mécanisme
(déjà fait — 1 carte testée avec succès le 20 août 2026), la migration complète des 281 cartes
actives est repoussée **au plus près possible du go-live**, sur un export gift cards fraîchement
tiré de Magento — voir [Chèques cadeaux](./gift-cards.md) pour le détail du risque (carte
utilisée/soldée entre l'export et l'import) et la recommandation de geler brièvement les
gift cards côté Magento (checkout + émission) pendant la fenêtre de migration finale.

---

## Phase 1 — Foundation

**Objectif :** les deux boutiques Shopify opérationnelles avec leur catalogue complet.

- Créer les deux boutiques Shopify (Dandoy-Sports Shopify Plus, Butterfly TT plan Basic)
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
| Export Magento final (produits, clients, commandes, clubs, gift cards) | Données fraîches J-2 |
| Régénérer CSV (`regenerate_all.sh`) | ~10 min, génère les fichiers des 2 boutiques (hors gift cards, script API séparé) |
| Réimporter produits — MERGE | Dans chaque boutique — met à jour prix, stocks, descriptions |
| Réimporter clients — MERGE | Dans chaque boutique — intègre les nouveaux comptes depuis la 1ère synchro |
| Réimporter Companies — MERGE (Dandoy uniquement) | Intègre les nouvelles adhésions club depuis la 1ère synchro — voir [Remises club & B2B](../mapping/club-b2b.md) |
| Import commandes | `shopify_orders_dandoy.csv` (24 896) / `shopify_orders_butterfly.csv` (14 198) — MERGE, intègre les commandes passées depuis la 1ère synchro |
| Import redirections 301 | `shopify_redirects_dandoy.csv` (2 045) / `shopify_redirects_butterfly.csv` (380) — MERGE |
| Migration chèques cadeaux — API | `migrate_giftcards_shopify.py --execute` sur un export gift cards fraîchement tiré (281 cartes actives, ~9 250 €) — voir [Chèques cadeaux](./gift-cards.md) |
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
| 2 | `shopify_products_{store}.csv` | Phase 1, réimporté à neuf en Phase 4 (MERGE) |
| 3 | `shopify_collections_{store}.csv` | Phase 1, réimporté à neuf en Phase 4 (MERGE) |
| 4 | `shopify_translations_{store}.csv` | Phase 1, réimporté à neuf en Phase 4 (MERGE) |
| 5 | `shopify_customers_{store}.csv` | 1ère synchro complète (dès que possible), resynchronisé à neuf en Phase 4 (MERGE) |
| 6 | `shopify_companies_dandoy.csv` | 1ère synchro complète (Dandoy uniquement), resynchronisé à neuf en Phase 4 (MERGE) |
| 7 | `shopify_orders_{store}.csv` | 1ère synchro complète, resynchronisé à neuf en Phase 4 (MERGE) |
| 8 | `shopify_redirects_{store}.csv` | Phase 4 (J-2), MERGE |
| 9 | Chèques cadeaux (API, `migrate_giftcards_shopify.py`) | Échantillon test dès maintenant, migration complète au plus près du go-live (pas de MERGE — code déjà pris si relancé) |

Tous les fichiers CSV (2–8) peuvent être réimportés autant de fois que nécessaire (MERGE),
y compris en Phase 4 pour synchroniser les nouveautés accumulées depuis la 1ère synchro. Seuls
les chèques cadeaux (9) suivent une logique à part — voir ci-dessus.

---

## Décisions en attente avant de démarrer

| Sujet | Statut |
|---|---|
| **Multi-sites** : instance unique ou deux boutiques ? | **Tranché** — Option B (deux boutiques séparées), décidé le 29 juillet 2026 |
| **Plan Shopify** : Basic / Shopify / Advanced / Plus ? | **Tranché** — Dandoy-Sports Shopify Plus, Butterfly TT plan Basic |
| **Limitations du plan Basic (Butterfly)** | À vérifier avant validation finale (rapports pro, shipping tiers calculé, comptes staff) |
| **Thème** : thème premium du marché ou développement sur mesure ? | À décider — conditionne le planning Phase 2 (× 2 thèmes à prévoir) |
| **Companies B2B (clubs partenaires)** | **Tranché pour Dandoy** (Shopify Plus confirmé, 85 companies prêtes) — Butterfly bloqué par la limite de 3 catalogues du plan Basic (4 nécessaires), décision client en attente — voir [Remises club & B2B](../mapping/club-b2b.md) |
| **Migration chèques cadeaux** | **Tranché** — Option B (API, codes préservés), test live confirmé le 20 août 2026 — voir [Chèques cadeaux](./gift-cards.md) |
| **Stratégie de synchro clients/commandes/companies en 2 passes** | **Tranché (20 août 2026)** — 1ère synchro complète dès maintenant, resynchro à neuf (MERGE) juste avant le go-live |
