# Doublons de variantes à corriger (Magento)

Liste des combinaisons d'options identiques détectées entre deux variantes d'un même
produit après régénération du CSV (`validate_shopify_csv.py`). Ce ne sont pas des bugs
du script de conversion : ce sont de vraies incohérences dans les données source
Magento (deux SKU partageant la même taille/couleur sans attribut distinctif), qui font
échouer l'import Matrixify avec l'erreur *"The variant '...' already exists."*.

Fichier source (CSV, non gitignoré) : `02_ANALYSIS_AND_MAPPING/doublons_variantes_a_corriger.csv`

---

## Action requise côté Magento

Pour chacune des paires ci-dessous, fusionner les deux SKU ou identifier l'attribut
manquant qui devrait les différencier (ex. un second coloris, une variante de poids,
un âge pour les tailles enfant) avant le prochain import complet.

| # | Handle | SKU 1 | SKU 2 | Valeur dupliquée |
|---|---|---|---|---|
| 1 | `stiga-hybrid-wood-nct` | 10000 | 10002 | Straight |
| 2 | `donic-shirt-orbit-flex-grey-white` | 25203 | 25223 | 5XL |
| 3 | `butterfly-tracksuit-jacket-move-grey` | 12884 | 12885 | S |
| 4 | `butterfly-polo-kuma-navy` | BTY20904 | BTY20905 | XS |
| 5 | `butterfly-shirt-nash-blue` | 25552 | 25553 | XS |
| 6 | `butterfly-shirt-nash-red` | BTY20948 | 25531 | XS |
| 7 | `butterfly-polo-germany-2015-zwart` | BTY30130 | BTY30131 | S |
| 8 | `butterfly-energy-force-xii` | 26359 | BTY55215 | 46 |
| 9 | `butterfly-t-shirt-tenergy-blue` | BTY28382 | 25677 | XS |
| 10 | `butterfly-t-shirt-ryo-red` | 25951 | 25952 | XS |
| 11 | `butterfly-lezoline-rifones-lime` | BTY55418 | BTY55416 | 34 |
| 12 | `joola-shirt-ace-lady-red-black` | 33948 | 33949 | XS |
| 13 | `joola-shirt-ace-lady-black-petrol` | 33962 | 33963 | XS |
| 14 | `joola-skirt-mara-black` | 34749 | 34750 | XS |
| 15 | `dsports-bas-liga-marine-blanc` | F4061 | F4062 | S |
| 16 | `dsports-bas-liga-blanc-royal` | F4092 | F4093 | M |
| 17 | `joola-shoes-nextt-20-navy-lime` | 26387 | 26388 | 44 |
| 18 | `butterfly-polo-higo-zwart` | 43178 | 43179 | 3XL |
| 19 | `ping-pang-t-shirt-justesse-navy` | 90570 | 90571 | M |
| 20 | `andro-short-torin-blue` | 91064 | 91065 | XL |
| 21 | `donic-double-bat-cover-pop` | 93005 | 93006 | Black |
| 22 | `andro-double-wallet-maboon` | 93267 | 93268 | Pink |
| 23 | `andro-double-wallet-maboon` | 93266 | 93269 | Blue |
| 24 | `andro-basic-wallet-maboon` | 93264 | 93265 | Blue |
| 25 | `butterfly-shirt-puren-zwart` | 92750 | 92751 | XS |
| 26 | `andro-batcover-round-moriva` | 97023 | 97024 | Black |
| 27 | `andro-batcover-round-moriva` | 97023 | 97025 | Black |
| 28 | `andro-batwallet-double-moriva` | 97026 | 97027 | Black |
| 29 | `stiga-short-basic-navy` | 96987 | 98540 | 3XL |
| 30 | `butterfly-sock-yonago-grey` | 97766 | 97767 | Grey |
| 31 | `butterfly-sock-yonago-grey` | 97766 | 97768 | Grey |
| 32 | `butterfly-sock-yonago-grey` | 97766 | 97769 | Grey |
| 33 | `tibhar-single-cover-spectra` | 97911 | 97912 | Blue |
| 34 | `tibhar-double-cover-spectra` | 97915 | 97916 | Blue |
| 35 | `tibhar-round-cover-spectra` | 97919 | 97920 | Blue |
| 36 | `tibhar-round-cover-with-ball-compartment-spectra` | 97923 | 97924 | Blue |

32 produits distincts (certains ont 2-3 doublons : `andro-batcover-round-moriva`,
`butterfly-sock-yonago-grey`, `andro-double-wallet-maboon`).

Confirmé lors du test Matrixify sur le catalogue complet (25 514 lignes, 272 échecs, avant le
passage à deux boutiques séparées) : ces 36 paires représentaient 246 des 272 lignes en échec.

> **Depuis le passage à l'Option B (deux boutiques)**, la validation locale
> (`validate_shopify_csv.py`) rapporte ces mêmes doublons répartis par boutique :
> 61 erreurs bloquantes sur Dandoy-Sports (4 183 produits), 14 sur Butterfly TT (849 produits) —
> essentiellement les mêmes paires ci-dessus, désormais comptées côté Dandoy et/ou Butterfly
> selon le catalogue où le produit apparaît. Voir [Avancement](../avancement.md).
