# Migration Clients — Magento → Shopify

---

## Données source

| Fichier Magento | Lignes | Contenu |
|---|---|---|
| `export_customer.csv` | 47 113 | Comptes clients (email, nom, mot de passe, website…) |
| `export_customer_address.csv` | 32 163 | Adresses (rue, ville, pays, téléphone…) |

---

## Résultat de la conversion

**Deux boutiques Shopify (Option B)** : le script écrit un fichier client par boutique. Les
clients présents sur les deux marques (tag `dandoy` **et** `butterfly`) sont dupliqués dans
les deux fichiers — un compte est nécessaire dans chaque boutique.

| Donnée | Dandoy-Sports | Butterfly TT |
|---|---|---|
| Clients exportés | **30 941** | **11 558** |
| Avec adresse | 19 663 | 8 315 |
| Sans adresse | 11 278 | 3 243 |

47 113 comptes Magento → 41 578 emails uniques après déduplication par email (le script garde
le compte le plus récemment mis à jour et fusionne les tags de source), puis **2 919 comptes
spam exclus** (voir [Nettoyage des données](#nettoyage-des-données-téléphone-province-pays-noms)
ci-dessous), soit 38 659 clients réels répartis dans les deux fichiers ci-dessus (la somme
dépasse ce total car les clients partagés entre les deux marques apparaissent dans les deux
fichiers).

### Tags source

Chaque client reçoit un tag indiquant son website d'origine :

| Tag | Clients uniques | Source Magento |
|---|---|---|
| `dandoy` | 30 941 | `base` + `ds_ww` |
| `butterfly` | 11 558 | `bt_be` + `bt_nl` |

Les clients présents sur les deux marques ont les deux tags et sont écrits dans les deux
fichiers (`shopify_customers_dandoy.csv` et `shopify_customers_butterfly.csv`).

### Répartition par pays (top 5, Dandoy-Sports)

| Pays | Clients |
|---|---|
| Belgique | 4 728 |
| France | 3 613 |
| USA | 1 524 |
| Pays-Bas | 1 436 |
| Brésil | 747 |

---

## Mapping des champs

| Magento | Shopify | Note |
|---|---|---|
| `email` | **Email** | Clé de déduplication |
| `firstname` | **First Name** | |
| `lastname` | **Last Name** | |
| `_website` | **Tags** | Converti en `dandoy` / `butterfly` |
| `is_review_booster_subscriber` | **Accepts Email Marketing** | `1` → `yes` |
| `telephone` (adresse) | **Phone** | Depuis l'adresse par défaut |
| `street` | **Address1** / **Address2** | Split sur retour à la ligne |
| `city` | **Address City** | |
| `postcode` | **Address Zip** | |
| `country_id` | **Address Country Code** | Code ISO (BE, FR, NL…) |
| `region` | **Address Province** | |
| `company` | **Address Company** | |
| `_address_default_billing_` | **Address Default** | Adresse par défaut billing en priorité |

### Sélection de l'adresse

Chaque client peut avoir plusieurs adresses dans Magento (max constaté : 88).
Le script sélectionne **une seule adresse** par ordre de priorité :

1. Adresse default billing
2. Adresse default shipping (si pas de billing)
3. Première adresse trouvée (si aucune par défaut)

---

## Nettoyage des données (téléphone, province, pays, noms)

Un premier import Matrixify réel (21 août 2026) a révélé 13 588 échecs sur 33 770 clients
(40 %) — Magento n'a jamais imposé de format sur ces champs, Shopify/Matrixify si. Le script
corrige maintenant ces 4 causes à la génération ; un second import sur le fichier corrigé n'a
laissé que 231 échecs résiduels (0,75 %), tous listés ci-dessous comme limitations connues.

| Problème Matrixify | Cause | Correction |
|---|---|---|
| `Phone is invalid` | Numéros Magento en format local brut (`0496/28.57.43`, `0032 471 48 99 07`) | Validation réelle via la lib `phonenumbers` (libphonenumber) + normalisation E.164, région déduite de `country_id`. Un numéro non récupérable est vidé plutôt que de faire échouer toute la ligne client. |
| `Province is invalid` | `region` Magento est du texte libre — même une vraie région échoue si elle ne correspond pas exactement à la liste Shopify (diacritiques, ancien nom, variante d'orthographe : `Bucureşti`, `Aiti` pour Aichi, `Yukon Territory` au lieu de `Yukon`…) | **Province envoyée uniquement pour les US** (`PROVINCE_SAFE_COUNTRIES` dans le script) — seul pays sans aucun échec observé sur deux campagnes de test live. Partout ailleurs, `Address Province` est vidée plutôt que de risquer l'échec au prochain import. |
| `"Address: Country Code" is not valid` | Pays obsolètes/inhabités (`AN`, `AQ`, `TF`, `HM`…) ou territoires US traités par Shopify comme des états (`PR`, `GU`, `AS`) plutôt que des pays | Adresse ignorée pour ces codes pays (`UNSUPPORTED_COUNTRIES`) — le client est quand même importé, sans adresse par défaut. |
| `First/Last name cannot contain URL` | 2 919 comptes bot historiques avec du texte spam/publicitaire dans les champs nom | **Compte exclu entièrement** du CSV (ce ne sont pas de vrais clients) — voir [Comptes spam exclus](#comptes-spam-exclus) ci-dessous. |
| `Address1 is too long` | Quelques adresses avec du texte publicitaire collé (limite Matrixify : 255 caractères) | Troncature à 255 caractères. |

**Limitation connue, non corrigeable depuis le CSV seul :** `Phone has already been taken` —
deux comptes différents partagent un numéro déjà présent côté Shopify suite à un import
antérieur (Phase 1). Le script déduplique déjà les téléphones *au sein* du fichier généré
(1er client rencontré garde le numéro, les suivants avec le même numéro passent avec `Phone`
vide) mais ne peut pas savoir ce qui existe déjà en base Shopify sans interroger l'API live.

Ces règles sont documentées dans le code (`magento_to_shopify_customers.py`, constantes
`UNSUPPORTED_COUNTRIES` / `PROVINCE_SAFE_COUNTRIES` / `SPAM_NAME_RE`), partagées avec
[la conversion des commandes](orders.md) (même logique d'adresse), et revalidées
automatiquement à chaque régénération par `validate_shopify_csv.py`.

Dépendance ajoutée : `phonenumbers` (voir `02_ANALYSIS_AND_MAPPING/SCRIPTS/requirements.txt`
— première dépendance externe du pipeline, jusque-là 100% stdlib Python). Installer avant de
lancer le script : `pip3 install -r 02_ANALYSIS_AND_MAPPING/SCRIPTS/requirements.txt`
(ajouter `--break-system-packages` si `pip` refuse l'install système sur Debian/Ubuntu).

### Comptes spam exclus

2 919 comptes créés côté Magento avec des liens/texte publicitaire directement dans les
champs `firstname`/`lastname` (ex. "Passives Einkommen Vor 8945 Euro..." avec un lien
raccourci) — des inscriptions bot, pas de vrais clients. Détectés par un pattern
URL/HTML (`SPAM_NAME_RE`) et exclus entièrement du CSV de sortie plutôt que d'importer une
fiche client inutilisable. Si un nom d'adresse (`Address First/Last Name`, distinct du nom
client) est seul touché, il est vidé sans exclure le reste de la fiche.

---

## Ce qui n'est PAS migré

### Mots de passe

Les `password_hash` Magento utilisent un algorithme de hachage **incompatible**
avec Shopify. Il n'existe aucun moyen de transférer les mots de passe.

**Conséquence :** tous les clients devront réinitialiser leur mot de passe
à la première connexion sur Shopify via le lien "Forgot password".

**Recommandation :** envoyer un email de bienvenue après la migration avec
un lien de réinitialisation. Shopify permet d'envoyer un "account invite"
en masse via l'admin ou via l'API.

### Adresses secondaires

Seule l'adresse par défaut est migrée. Les 4 615 clients avec plusieurs
adresses perdront leurs adresses secondaires. Ils pourront les recréer
dans leur espace client Shopify.

### Historique des commandes

Les commandes passées ne sont pas incluses dans cet export.
Une migration séparée serait nécessaire via l'export Magento des commandes.

### Données non pertinentes

| Champ Magento | Raison d'exclusion |
|---|---|
| `password_hash` | Incompatible avec Shopify |
| `dob` (date de naissance) | Shopify ne gère pas ce champ nativement |
| `gender` | Vide pour 98% des clients |
| `taxvat` | 1 seul client renseigné |
| `group_id` | Groupes clients Magento non migrés |
| `inchoo_socialconnect_*` | Tokens de connexion sociale — non transférables |
| `zd_user_id` | ID Zendesk — reconfigurer côté Zendesk si utilisé |

---

## Import dans Shopify

### Via Matrixify

1. Dans Matrixify (boutique Dandoy-Sports), cliquer **Import**
2. Uploader `shopify_customers_dandoy.csv`
3. Lancer l'import
4. Répéter avec `shopify_customers_butterfly.csv` dans la boutique Butterfly TT

**Vérification :** ouvrir quelques clients dans Shopify Admin → Customers et vérifier :
- Nom, email, téléphone
- Adresse par défaut
- Tags (dandoy / butterfly)
- Statut marketing

### Via l'import natif Shopify

Shopify permet aussi d'importer des clients via **Customers → Import**.
Le format est compatible mais Matrixify offre plus de contrôle (commandes MERGE/UPDATE).

---

## Post-migration

### Invitation clients

Après l'import, envoyer une invitation de création de mot de passe :

**Option 1 — En masse via Shopify Admin :**

Customers → Select all → Actions → Send account invite email

**Option 2 — Via l'API Shopify (pour plus de contrôle) :**

```
POST /admin/api/2024-01/customers/{id}/send_invite.json
```

### Communication

Préparer un email de migration informant les clients :
- Nouveau site, même catalogue
- Nécessité de réinitialiser le mot de passe
- Lien direct vers la page "Forgot password"

---

## Script

```bash
python3 02_ANALYSIS_AND_MAPPING/SCRIPTS/magento_to_shopify_customers.py
```

Inclus dans `regenerate_all.sh` (étape 4/9). Génère les deux fichiers en une seule exécution.
Source : `01_DATA_RAW/export_customer.csv` + `01_DATA_RAW/export_customer_address.csv`

Nécessite `phonenumbers` (voir [Nettoyage des données](#nettoyage-des-données-téléphone-province-pays-noms) ci-dessus).
