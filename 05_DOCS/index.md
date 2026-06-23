# Migration Dandoy-Sports → Shopify

Documentation technique de la migration Magento 2 vers Shopify pour **Dandoy-Sports / Butterfly TT**.

---

## Périmètre

- **Client :** Dandoy-Sports / Butterfly TT
- **6 domaines :** dandoy-sports.com, fr/en/nl.dandoy-sports.eu, be.butterfly.tt, nl.butterfly.tt
- **3 langues :** Anglais (défaut), Français, Néerlandais
- **Catalogue :** 4 834 produits, 19 metafields, 37 collections

## Fichiers d'import prêts

| Fichier | Contenu | Lignes |
|---|---|---|
| `shopify_products.csv` | Produits EN + metafields + tags | 25 514 |
| `shopify_translations.csv` | Traductions FR + NL | 6 723 |
| `shopify_collections.csv` | 37 smart collections | 58 |
| `shopify_redirects.csv` | Redirections 301 | 2 368 |

## Ordre d'import

1. **Produits** → Collections → Langues (activer FR/NL) → **Traductions** → **Redirections**

## Régénération

Après mise à jour de l'export Magento :

```bash
bash 02_ANALYSIS_AND_MAPPING/SCRIPTS/regenerate_all.sh
```

Des fichiers `*_PURGE.csv` sont aussi générés pour repartir à zéro entre tests (import via Matrixify avec commande DELETE).

## Navigation

- [Quick Start — Mode d'emploi](./quick-start.md)
- [Avancement du projet](./avancement.md)
- [Matrice de mapping](./mapping/matrice.md)
- [Metafields](./mapping/metafields.md)
- [Multi-sites](./architecture/multi-sites.md)
- [Guide prestataire stock](./stock/guide-prestataire.md)
