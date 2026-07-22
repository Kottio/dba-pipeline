# Cleaned Notes — DBuilders Pipeline
*(Notetaking.md, tidied for re-reading. Same content, same voice, typos fixed.)*

## 17/07 — Planification & Phase 0

Planification de la pipeline avec Claude.

**Création du repo par Claude :**
- ✅ Création des dossiers importants pour GitHub.
- ❌ Création de beaucoup de fichiers que je ne comprends pas : `.sqlfluff`, `docker-compose` déjà écrit, `.github/workflows` créé sans explication ni communication.
- ❌ Trop de décisions prises d'avance, sans évolution au fur et à mesure.

**Décision :** demander à Claude ce que sont ces fichiers, puis les supprimer — le projet doit grandir organiquement.

**Actions faites :**
- Supprimé : docker-compose, GitHub workflow.
- Dans le projet uv : supprimé les dépendances écrites avant même d'avoir travaillé dessus.
- `.sqlfluff` sera recréé quand on en aura besoin.
- Reset du git : supprimé le `.git` créé par Claude, refait `git init` moi-même.

**Changements de plan :**
- On ne monte sur le Droplet que quand le projet marche déjà en local (optimiser les coûts).
- Ordre clarifié : local → GitHub → Droplet.
- Ajouté le plan complet du projet dans le repo pour guider Claude.

## 17/07 — Phase 1 : Infra / dépendances

- Changement du plan : **aucun container Docker nécessaire pour l'instant**. Seulement les dépendances Python et les autres technos.
- Dû expliquer à Claude que **dbt Fusion n'est pas du Python** (c'est un binaire Rust) — l'IA n'est pas toujours à jour.
- Dû pousser le fait que **dbt Fusion fonctionne avec DuckDB** (je l'ai installé et testé moi-même).
- **Leçon claire : ne pas laisser Claude décider sur des suppositions — tester soi-même.**

## 17/07 — Test dbt Fusion + DuckLake (dossier first_Test)

**Créer le lake depuis DuckDB :**
```sql
-- duckdb dev.duckdb
INSTALL ducklake;
ATTACH 'ducklake:my_ducklake.ducklake' AS my_ducklake;
USE my_ducklake;

CREATE SCHEMA my_lake;
CREATE TABLE my_lake.test_table AS
  SELECT 1 AS id, 'hello ducklake' AS name, now() AS created_at
  UNION ALL
  SELECT 2, 'second row', now();

SELECT * FROM my_lake.test_table;
```

**Config dbt — les 3 fichiers à aligner :**

1. `profiles.yml` — attacher le ducklake :
```yaml
outputs:
  ducklake:
    type: duckdb
    path: dev.duckdb
    attach:
      - path: "ducklake:my_ducklake.ducklake"
        alias: my_ducklake
```

2. `dbt_project.yml` — cibler cette database via l'alias :
```yaml
models:
  dbt_ducklake:
    +database: my_ducklake
```

3. `sources.yml` — expliciter la database aussi :
```yaml
sources:
  - name: my_lake
    database: my_ducklake
    tables:
      - name: test_table
```

**Accès au ducklake :** toujours via duckdb + `ATTACH 'ducklake:my_ducklake.ducklake'`.

**Modèle mental à garder :**
```
DuckDB     = le moteur (un programme qui exécute du SQL)
DuckLake   = la mémoire (fichiers Parquet + un catalogue qui les indexe)
ATTACH 'ducklake:...' = la clé qui connecte moteur et mémoire
les views vivent dans le catalogue · les tables vivent en Parquet
```

---

## 20/07 — uv, dlt, et le lac partagé (sandbox : prior-testing/dbt-ducklake)

### Setup uv (once)

```bash
uv init --bare                      # pyproject.toml + .python-version, no hello-world noise
uv add "dlt[postgres,ducklake]"     # first dependency, at its moment → creates .venv + uv.lock
source .venv/bin/activate           # or prefix everything with `uv run`
```

- Extras = connectors for what dlt talks to: `postgres` (read source) · `ducklake` (write destination).
- Commit: `pyproject.toml`, `uv.lock`, `.python-version`. Never: `.venv/`.
- `dlt --version` fails bare → it lives in the venv: `uv run dlt --version` (or activate).

### dlt scaffold

```bash
dlt init foo ducklake     # template pipeline + .dlt/{config,secrets}.toml
```

The scaffolded `secrets.toml` is a *menu*, not a form → delete everything you don't use.

### The working config — `.dlt/secrets.toml`

```toml
[destination.ducklake.credentials]
ducklake_name = "my_ducklake"
catalog = "duckdb:///my_ducklake.ducklake"       # THREE slashes!

[destination.ducklake.credentials.storage]
bucket_url = "file:///Users/kottio/KottioDev/DBuilders_pip/prior-testing/dbt-ducklake/my_ducklake.ducklake.files/"
```

Naming trap: `destination="ducklake"` in the pipeline = the *type* (fixed menu).
`ducklake_name` = free internal attach alias. Config section addressed by *type*.

### The minimal pipeline

```python
import dlt

pipeline = dlt.pipeline(
    pipeline_name="foo",
    destination="ducklake",
    dataset_name="lake_schema",   # = schema created in the lake
    # dev_mode=True → adds a timestamp suffix to the schema EVERY run. Only for demos.
)
info = pipeline.run([{"foo": 1}, {"foo": 2}], table_name="table_foo")
```

### The five failure modes (each one a lesson)

1. **`duckdb://file` (2 slashes) = hostname, not path** → dlt silently created a twin catalog
   (`my_ducklake.duckdb`). Fix: `duckdb:///file` — 3 slashes = local path.
2. **CLI lock**: an open duckdb shell holds the file-catalog lock → dlt can't write.
   Close sessions before runs. (Prod answer: catalog in Postgres = polite row-level locks.)
3. **Frozen DATA_PATH**: the catalog stores its storage path *absolute, at creation*.
   Renaming the folder (first_Test → prior-testing) broke it. Repair:
   `ATTACH 'ducklake:cat.ducklake' AS l (DATA_PATH '/new/path/', OVERRIDE_DATA_PATH TRUE);`
   → real-project rule: create `data/` in its final home, never rename it.
4. **Twin catalogs**: x-rayed the wrong file (`.duckdb` vs `.ducklake`) → contradictory diagnostics.
   When confused: `SELECT * FROM ducklake_metadata;` on the *plain-opened* catalog tells the truth.
5. **Stray keystroke** (`}}m`) in a model → dbt Parser Error. Read the error's line/column.

### Rebuild from zero (the sequence that worked)

```bash
rm my_ducklake.ducklake my_ducklake.duckdb dev.duckdb
rm -rf my_ducklake.ducklake.files
dlt pipeline foo drop-pending-packages

# birth the lake EXPLICITLY (data path declared, final home)
duckdb -c "ATTACH 'ducklake:my_ducklake.ducklake' AS lake (DATA_PATH '/Users/kottio/KottioDev/DBuilders_pip/prior-testing/dbt-ducklake/my_ducklake.ducklake.files/');"

# source table by hand
duckdb -c "
ATTACH 'ducklake:my_ducklake.ducklake' AS lake;
CREATE SCHEMA lake.my_lake;
CREATE TABLE lake.my_lake.test_table AS
  SELECT 1 AS id, 'hello ducklake' AS name, now() AS created_at
  UNION ALL SELECT 2, 'second row', now();"

dbt run                    # dbt Fusion → stg_test_table into the lake
python foo_pipeline.py     # dlt → table_foo into the SAME lake

duckdb -c "ATTACH 'ducklake:my_ducklake.ducklake' AS l; SHOW ALL TABLES;"
```

**Result: one catalog, three makers** — `my_lake.test_table` (hand), `main.stg_test_table` (dbt),
`lake_schema.table_foo` + `_dlt_*` flight-recorder tables (dlt).

### dbt sources across schemas

One `sources:` block per schema; `name` = logical label, `schema` = physical address:

```yaml
sources:
  - name: my_lake
    database: my_ducklake
    schema: my_lake
    tables: [{name: test_table}]
  - name: dlt_raw
    database: my_ducklake
    schema: lake_schema        # dlt's dataset_name (stable once dev_mode is off)
    tables: [{name: table_foo}]
```

---

## 20/07 — INFRA du vrai repo : naissance du lac + setup serveur

### `infra/ducklake-setup.sh` — l'acte de naissance du lac

Le lac de production locale est créé par un script versionné, pas par des commandes oubliées :

```bash
mkdir data
duckdb -c "INSTALL ducklake;"
duckdb -c "ATTACH 'ducklake:data/lake_catalog.ducklake' AS datalake (DATA_PATH 'data/lake_files/');"
```

- **Pourquoi un script** : la création du lac est un *événement explicite*, documenté, rejouable —
  sur le droplet ce sera exactement le même : `git clone` → `./infra/ducklake-setup.sh`.
- `data/` est **gitignoré** : le lac ne voyage jamais par git, il se reconstruit par la recette.
- `DATA_PATH` déclaré = pas de chemin implicite ; créé dans son **emplacement définitif** (leçon du chemin gelé).
- Améliorations à faire (appris depuis) : `#!/usr/bin/env bash` + `set -euo pipefail` en tête,
  `mkdir -p` (idempotent — rejouable sans erreur), `chmod +x`.

### `infra/setup_server.sh` — la recette de tout ce qui n'est PAS dans uv (à créer)

Décision : les binaires hors-uv (duckdb CLI, dbt Fusion, uv lui-même) ont besoin de leur propre
recette d'installation. uv gère `uv.lock` pour Python ; le reste va dans `setup_server.sh` :

```bash
# duckdb CLI 1.5.4 · dbt Fusion 2.0.0-preview.196 (versions épinglées !)
# aujourd'hui : lisible par un humain (moi, un étudiant, le droplet)
# demain : première ébauche du Dockerfile de prod
```

Trois couches de recettes, désormais complètes :
1. Python → `pyproject.toml` + `uv.lock` (`uv sync`)
2. Binaires/machine → `infra/setup_server.sh` + README Prerequisites
3. Le lac lui-même → `infra/ducklake-setup.sh`

---

## 21/07 — L'EXAMEN : refaire le pipeline from scratch (SecondFullTest)

Refait le pipeline de zéro, en solo. J'ai galéré — et c'est là que ça s'est ancré.
Claude s'est trompé plusieurs fois sur les chemins ; **il a fallu tester moi-même pour que ça marche.**

### Setup (les commandes qui restent)

```bash
uv init --bare
uv add "dlt[ducklake]"          # (+ postgres quand la vraie source arrivera)
uv run dlt init foo ducklake    # scaffold .dlt/{config,secrets}.toml
```

### La règle d'or découverte en galérant

Le catalogue enregistre son DATA_PATH **à la naissance, tel quel** (relatif reste relatif,
absolu reste absolu). dlt **annonce toujours** un chemin (le sien par défaut : `<cwd>/<ducklake_name>.files/`).
**naissance et annonce doivent être identiques octet par octet** — sinon : `DATA_PATH does not match`.

### Les 4 mondes qui marchent (testés)

1. **dlt crée le lac lui-même** (pas de création manuelle, pas de [storage]) — simple mais
   le lac naît en effet de bord, chemin dicté par l'outil. Fragile (dépend du cwd du premier run).
2. **Chemin par défaut, annoncé** : création manuelle SANS DATA_PATH → le catalogue enregistre
   le défaut absolu (`<catalog>.files/` adjacent) → `bucket_url` copie exactement cette chaîne :

```bash
mkdir data
duckdb -c "ATTACH 'ducklake:data/my_ducklake.ducklake' AS lake;"   # sans DATA_PATH
```
```toml
[destination.ducklake.credentials]
ducklake_name = "my_ducklake"
catalog = "duckdb:///data/my_ducklake.ducklake"
[destination.ducklake.credentials.storage]
bucket_url = "file:///.../SecondFullTest/data/my_ducklake.ducklake.files/"   # = le défaut, absolu
```

3. **Tout relatif** : DATA_PATH relatif à la naissance + bucket_url relatif — marche,
   MAIS tout doit toujours tourner depuis le même dossier :

```bash
duckdb -c "ATTACH 'ducklake:data/lake.ducklake' AS lake (DATA_PATH 'data/lake_files');"
```
```toml
bucket_url = "file:data/lake_files/"    # URL relative — borderline, ne pas enseigner
```

   ⚠️ **Le piège du relatif** : depuis un autre dossier, le même ATTACH crée silencieusement
   un NOUVEAU lac vide (pas d'erreur !). dbt tourne depuis transform/, Dagster depuis ailleurs →
   en multi-outils le relatif casse.

4. **Absolu explicite, calculé** — le pattern de prod : `DATA_PATH '$(pwd)/data/lake_files/'`
   dans le script de setup, la même chaîne (préfixée `file://`) dans chaque client via `.env`.
   Déclaré, absolu, portable. **C'est celui du vrai repo.**

### Pièges divers de la session

- `destination="ducklake"` = le TYPE (menu fixe) — pas le nom du lac (régression faite et corrigée).
- 3 lignes dans table_foo = mes 3 items de test, pas un mystère append.
- `/data/...` avec slash initial = racine du Mac, pas le dossier du projet !
- Vérif avant de lancer : `duckdb <catalog> -c "SELECT value FROM ducklake_metadata WHERE key='data_path';"`

### Reste à faire pour finir l'examen

dbt : profile attach, sources (dont `lake_schema.table_foo` de dlt), un modèle dans le lac,
`SHOW ALL TABLES` → trois artisans, un lac.

---

## 📌 RÉCAP — tout ce qu'on a vu jusqu'ici

**Le modèle mental (4 lignes) :**
```
DuckDB    = le moteur (un programme qui exécute du SQL)
DuckLake  = la mémoire (Parquet + un catalogue qui les indexe)
ATTACH 'ducklake:...' = la clé qui connecte moteur et mémoire
views → dans le catalogue · tables → en Parquet
```

**L'architecture prouvée :** Postgres prod → **dlt** → DuckLake (raw) → **dbt Fusion** (staging → marts) → plus tard Dagster, Evidence, MCP. Tous les outils entrent par la même clé `ATTACH 'ducklake:...'` — un lac, un catalogue, plusieurs mains.

**Les recettes par écosystème** (jamais le logiciel installé dans git, toujours la recette) :
Python → `pyproject.toml` + `uv.lock` (`uv sync`) · binaires (Fusion, duckdb CLI) → README Prerequisites, versions épinglées · plus tard prod → Dockerfiles. La data ne voyage JAMAIS par git : le lac se reconstruit en rejouant la recette.

**Les règles du projet :** git m'appartient (l'IA propose, j'exécute) · croissance organique (rien avant son moment, rien que je ne comprends pas) · décisions sur preuve, jamais sur supposition d'IA (Fusion, dlt[ducklake] : deux fois vérifié, deux fois l'IA corrigée) · sessions éphémères, seuls les fichiers restent · les erreurs se documentent (ai-log), elles sont le meilleur contenu.

**État : sandbox terminé, tout prouvé — et le vrai lac est né (`data/lake_catalog.ducklake`, via `infra/ducklake-setup.sh`). Prochaine étape : le vrai build** — lac `data/` dans le repo principal, ingestion réelle depuis le Postgres de la plateforme de cours (il reste à répondre : managé DO ou auto-hébergé ?).
