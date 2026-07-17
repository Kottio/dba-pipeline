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
