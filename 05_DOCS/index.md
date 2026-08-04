# Migration Dandoy-Sports → Shopify

Documentation technique de la migration Magento 2 vers Shopify pour **Dandoy-Sports / Butterfly TT**.

---

## Périmètre

- **Client :** Dandoy-Sports / Butterfly TT
- **Architecture :** deux boutiques Shopify séparées (Option B, décidée le 29 juillet 2026) — Dandoy-Sports (plan complet) et Butterfly TT (plan Basic). Détails : [Multi-sites](./architecture/multi-sites.md)
- **6 domaines répartis sur 2 boutiques :**
  - Dandoy-Sports : dandoy-sports.com, fr/en/nl.dandoy-sports.eu
  - Butterfly TT : be.butterfly.tt, nl.butterfly.tt
- **3 langues :** Anglais (défaut, Dandoy uniquement), Français, Néerlandais
- **Catalogue :** 4 834 produits uniques (dont 199 partagés entre les deux marques), 20 metafields, 37 collections

## Fichiers d'import prêts

Un jeu de fichiers par boutique — voir [Avancement](./avancement.md) pour le détail complet.

| Fichier | Contenu | Dandoy-Sports | Butterfly TT |
|---|---|---|---|
| `shopify_products_{store}.csv` | Produits EN + metafields + tags | 22 223 lignes | 4 905 lignes |
| `shopify_translations_{store}.csv` | Traductions FR + NL | 5 768 lignes | 1 233 lignes |
| `shopify_collections_{store}.csv` | 37 smart collections | 58 lignes | 58 lignes |
| `shopify_redirects_{store}.csv` | Redirections 301 | 2 045 lignes | 380 lignes |

## Ordre d'import (à répéter dans chaque boutique)

1. **Produits** → Collections → Langues (activer FR/NL, + EN pour Dandoy) → **Traductions** → **Redirections**

## Régénération

Après mise à jour de l'export Magento :

```bash
bash 02_ANALYSIS_AND_MAPPING/SCRIPTS/regenerate_all.sh
```

Régénère en une seule commande les fichiers des deux boutiques. Des fichiers `*_PURGE.csv` (×8, un par entité et par boutique) sont aussi générés pour repartir à zéro entre tests (import via Matrixify avec commande DELETE).

## Navigation

- [Quick Start — Mode d'emploi](./quick-start.md)
- [Avancement du projet](./avancement.md)
- [Matrice de mapping](./mapping/matrice.md)
- [Metafields — Définitions](./mapping/metafields-definitions.md)
- [Metafields — Choix prédéfinis](./mapping/metafields-choix-predefinis.md)
- [Metafields — Filtrage & Affichage](./mapping/metafields-filtrage.md)
- [Multi-sites](./architecture/multi-sites.md)
- [Guide prestataire stock](./stock/guide-prestataire.md)
