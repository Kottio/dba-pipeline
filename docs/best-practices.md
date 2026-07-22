# Best practices & reference repos

Practices adopted (or queued) for this project, with their source and their moment.
Rule unchanged: nothing enters the repo before its phase — this file is the waiting room.

## Reference repo: DataLabTechTV/datalab

https://github.com/DataLabTechTV/datalab — a YouTube channel's real data-lab platform
(DuckLake + dbt + dlt-adjacent stack, MinIO/S3, MLflow, KùzuDB). Our architecture,
photographed a few years in the future. Cloned as a *library*, outside this repo:
`~/KottioDev/references/datalab` — copy to understand, never wholesale.

### Adopt NOW (current phases)

- **`env_var()` in dbt profiles** — attach string as
  `"ducklake:{{ env_var('LAKE_CATALOG') }}"`, value in `.env`.
  Solves laptop-vs-droplet paths permanently: the variable travels, not the path.
  Same trick as `$(pwd)` in the setup script, generalized to all config.
- **`justfile` (command runner)** — named recipes replace memorized incantations
  (`just lakehouse` → REPL on the lake, `just init-lake`, `just pipeline`).
  Our `infra/*.sh` scripts graduate into it. Doubles as living documentation:
  read the justfile = know every operation the project supports.
- **`.env`-driven config everywhere** — one committed `.env.example`, per-machine `.env`.
- **Untracked local dir for data** (their `local/` = our `data/`) — already ours; validated.

### Study at the matching phase

- `ingest/` layout → when writing the real dlt pipeline (Phase 2)
- raw → stage → marts flow in `transform/` → Phase 3 modeling
- backup-to-S3 of embedded DBs → our backup story, droplet phase
- Postgres-catalog-as-secret in profiles → Phase 8 catalog migration preview

### Consciously NOT copied (scope, or different defensible choice)

- Kafka, MLflow, KùzuDB, A/B testing, Proxmox/Terraform — their years of accumulation,
  not our Phase 2. Each would need to pass the organic rule on its own merits, later.
- SQLite catalogs (they) vs duckdb-file → Postgres (us): both legitimate; ours keeps
  the Postgres end-state explicit.
- Object-storage-first (they) vs local-files-first, droplet later (us): cost and
  teaching-progression choice. `bucket_url`'s `file://` is the local dialect of theirs.

## Hard-won practices from our own sandbox (see Notes/Cleaned_Notes.md for the full stories)

- **Lake birth is explicit**: setup script, absolute DATA_PATH computed via `$(pwd)`,
  never a tool side effect. Birth string and every client's announcement: byte-identical.
- **Data never travels through git**; the recipe does. Three recipe layers:
  uv lock (Python) · setup-server.sh + README prerequisites (binaries, pinned) ·
  ducklake-setup.sh (the lake itself).
- **One catalog, many guests**: every tool holds the same attach string, from config.
- **Close CLI sessions** before pipeline runs (file-catalog locks) — until the
  Postgres catalog makes concurrency real.
- **Verify before running**: `SELECT value FROM ducklake_metadata WHERE key='data_path';`
- **AI proposes, human executes and verifies** — five AI errors in five days, all caught
  by testing against ground truth. Distrust correctly.
