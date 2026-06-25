# Migration Clients — Magento → Shopify

---

## Données source

| Fichier Magento | Lignes | Contenu |
|---|---|---|
| `export_customer.csv` | 46 423 | Comptes clients (email, nom, mot de passe, website…) |
| `export_customer_address.csv` | 31 548 | Adresses (rue, ville, pays, téléphone…) |

---

## Résultat de la conversion

| Donnée | Valeur |
|---|---|
| Clients exportés | **41 020** (dédupliqués par email) |
| Avec adresse | 25 006 |
| Sans adresse | 16 014 |
| Accepts Marketing | 21 104 |

### Déduplication

46 423 comptes Magento → 41 020 clients Shopify. La différence (5 403) vient
de clients inscrits sur **plusieurs websites** Magento (ex: base + bt_be) avec
le même email. Le script garde le compte le plus récemment mis à jour et
fusionne les tags de source.

### Tags source

Chaque client reçoit un tag indiquant son website d'origine :

| Tag | Clients | Source Magento |
|---|---|---|
| `dandoy` | 33 357 | `base` + `ds_ww` |
| `butterfly` | 11 404 | `bt_be` + `bt_nl` |

Les clients présents sur les deux marques ont les deux tags.

### Répartition par pays (top 5)

| Pays | Clients |
|---|---|
| France | 6 471 |
| Belgique | 5 822 |
| Pays-Bas | 2 846 |
| USA | 1 511 |
| Brésil | 746 |

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

1. Dans Matrixify, cliquer **Import**
2. Uploader `shopify_customers.csv`
3. Lancer l'import

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

Inclus dans `regenerate_all.sh` (étape 4/6).
Source : `01_DATA_RAW/export_customer.csv` + `01_DATA_RAW/export_customer_address.csv`
