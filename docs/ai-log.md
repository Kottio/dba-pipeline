# AI log — working with AI on this project

One honest entry per phase, minimum: one interaction that worked well, one that failed or needed correction. This is teaching material on the "AI does syntax, humans own semantics" discipline — the failures are the most valuable entries.

Workflow: Tom writes raw notes in `Notetaking.md` → Claude formats them here.

## Phase 0 — 2026-07-17

**Task given to AI:** plan the pipeline (research, architecture, build plan) and scaffold the repo (Claude, Cowork session).

**What it did well:**
- Planning: market research with sources; the DuckLake-vs-Postgres discussion surfaced the concurrency argument.
- Repo created with a sensible folder structure for GitHub.

**Where it went wrong / what the human had to correct:**
- Created many files the owner didn't understand: `.sqlfluff`, a `docker-compose.yml` already written before Phase 1 even started, `.github/workflows/ci.yml` created without explanation or discussion.
- Too many decisions taken upfront, instead of evolving step by step with the builder.
- The scaffold was *complete* but not *understood* — and an unexplained file is technical debt for a learning project.

**Correction applied:** delete the not-yet-understood files and let the project grow organically. Each file comes back only when its phase needs it, explained first, understood before committed.

**Applied by Tom (same day):**
- Deleted `docker-compose.yml`, the GitHub workflow, and the pre-written dependencies in `pyproject.toml` — each returns when its phase needs it.
- Deleted Claude's `.git` entirely (it was littered with stale lock files — the remote bridge can't delete git's temp files) and re-initialized it himself. New rule: **git runs only on the owner's machine**; the AI proposes commands, the human executes.
- Confirmed the local-first order: everything proven locally → GitHub → droplet last, to optimize cost.
- Brought the project plan into the repo to guide the work.

**Lesson:** an AI will happily build the whole house on day one. The human's job is pacing: nothing enters the repo that its owner can't explain. "AI does syntax, humans own semantics" also means humans own the *rhythm*.

> Note originale (FR) : « Création de beaucoup de fichiers que je ne comprends pas (…) Trop de décisions prises sans évolution au fur et à mesure. Je vais demander à Claude ce que sont ces fichiers et les supprimer pour que le projet grandisse organiquement. »

## Phase 1 prep — engine decision & DuckLake sandbox — 2026-07-17

**Task given to AI:** define what Phase 1 (dependencies/technologies) actually needs; validate the transform engine.

**What the human had to correct — the day's real lesson:**
- Claude assumed dbt = Python package. **dbt Fusion is a Rust binary** — not installed via uv, travels via a pinned version in README prerequisites. AI knowledge is not always current.
- Claude assumed Fusion+DuckDB support was uncertain. Tom installed it and proved it works, then pushed the decision through: **Fusion from the start** (ADR 0002).
- Pattern confirmed twice in one day: *never let the AI decide on assumptions — a 10-minute test beats its training data.* The human owns decisions; the AI provides context and gets verified.

**Also revised:** Phase 1 needs no Docker at all — Python deps via uv, Fusion as binary, DuckLake as files. Containers arrive only when a real service does (catalog Postgres, at concurrency time).

**Sandbox results (first_Test/) — what is now proven:**
- Fusion 2.0.0-preview.196 + DuckDB + DuckLake: `dbt debug` OK, `dbt run` green end-to-end (source in lake → model materialized back into lake).
- Traps found and understood on the way: a file *named* `.ducklake` attached via plain `path:` is just a native DuckDB file — only the `ducklake:` attach prefix makes a lake · `ref()` is for models, `source()` for external tables · views live in the catalog (no Parquet), tables write Parquet into `.files/`.

**Validated configuration (the trinity):**
1. `profiles.yml` — attach the lake: `attach: [{path: "ducklake:my_ducklake.ducklake", alias: my_ducklake}]`
2. `dbt_project.yml` — materialize into it: `models: <project>: +database: my_ducklake`
3. `sources.yml` — locate raw data in it: `database: my_ducklake` (+ `schema:` when source name ≠ schema)

**Mental model (keep):**
```
DuckDB    = the engine (a program that runs SQL)
DuckLake  = the memory (Parquet files + a catalog that indexes them)
ATTACH 'ducklake:...' = the key connecting engine to memory
views live in the catalog · tables live as Parquet
```

## Phase 1 — uv, dlt & the shared-lake proof — 2026-07-20

**Task:** set up uv from scratch; prove dlt can write into the same DuckLake that dbt Fusion uses (the one-lake architecture bet).

**What the AI got wrong (and the human caught):**
- Proposed `dlt[duckdb]` — Tom asked "duckdb, not ducklake?", forcing a doc check: dlt has a **native `ducklake` destination** with its own extra. Third instance of the pattern: *AI priors lag the ecosystem; verify before adopting.*

**What the collaboration did well:** five failures diagnosed in sequence without losing the thread — each error read carefully, root cause named, lesson extracted (3-slash URLs, file-catalog locks, frozen DATA_PATH, twin catalogs, stray keystroke). The AI proposed abandoning the broken sandbox ("bankruptcy"); Tom insisted on rebuilding until it worked — the right call: the rebuild-from-rubble is now the best-understood part of the stack.

**Proven:** one DuckLake, duckdb-format catalog, shared by three writers — manual SQL, dbt Fusion, dlt — verified side by side in `SHOW ALL TABLES`. The architecture's riskiest assumption is now fact.

**Also shipped (by Tom, solo):** the real lake's birth certificate — `infra/ducklake-setup.sh` created `data/lake_catalog.ducklake` in its final home — and the decision that all non-uv binaries (duckdb CLI, dbt Fusion) get their own recipe in `infra/setup_server.sh`, the future Dockerfile's first draft.

**Rules reinforced:** file catalogs hate concurrent sessions (the droplet's Postgres catalog is now justified by lived experience, not just ADR 0001) · create the lake explicitly, in its final home, DATA_PATH declared · `dev_mode` never in real pipelines.

## The Exam — sandbox rebuilt solo — 2026-07-21

**Task:** Tom rebuilds the whole dlt+DuckLake setup from scratch, from memory, to consolidate. AI on call only when surprised.

**What the AI got wrong (twice):**
- Claimed omitting dlt's `[storage]` block makes dlt defer to the catalog's recorded path. False — dlt *synthesizes* a default from `ducklake_name` and announces it (error #4).
- Claimed DuckLake resolves a relative DATA_PATH to absolute at creation. False — recorded verbatim (error #5).

**What the human did right:** refused to accept "it can't work without X" when memory said otherwise ("No, because before I made it work without the absolute path") — and was correct: the earlier success was dlt-as-creator, a different consistent world. Tested variants until the full map emerged: four consistent path configurations, each verified by hand. In Tom's words: *"Claude was struggling a lot with this — needed to test myself for it to work."*

**Outcome:** complete understanding of DuckLake path semantics (birth-time recording, byte-identical announcement, cwd traps), a production decision (`$(pwd)`-computed absolute paths in infra, mirrored via config), and the exam's dlt half passed without notes. dbt half remains.

**Meta-lesson for the log:** five AI errors in five days, every one caught by the human testing against ground truth. The collaboration works *because* the human distrusts correctly — this is the skill the mentoring should teach first.

## The Exam, part 2 — dbt half, and the alias collision — 2026-07-22

**Task:** finish the solo rebuild: dbt Fusion reading dlt's tables in the shared lake.

**The saga:** Fusion attached the lake as plain `duckdb` — invisible schemas, hours of hunting. The AI burned seven theories (orphan metadata wings, engine version skew, a Fusion .200 regression — refuted by Tom, who checked the timeline; dlt metadata formats; relative DATA_PATH). The decisive probes were real: `duckdb_databases()` type column, mtime forensics, a fresh-catalog differential test. But the answer was Tom's:

**Failure mode #7 — the alias collision.** DuckDB names a database after its filename stem: `path: data/lake.duckdb` enters the engine as database `lake`, colliding with `attach: alias: lake`. The scratch db wore the lake's name; the real DuckLake attach was shadowed. Every clue retrofits: the 17th worked (dev vs my_ducklake — no collision), `fresh` worked (unique alias), scratch mtime moved while the catalog's never did. **Rule: an attach alias must never equal the filename stem of the path database.**

**Also learned:** profile `schema:` sets the target's base schema cleanly; `+schema:` concatenates (`main_analytics`) until `generate_schema_name` is overridden — queued for the real transform/.

**Outcome: EXAM PASSED.** Lake with `lake_schema` (dlt) + `analytics` (dbt), rebuilt solo, every failure understood. The human found the final bug with the AI's own methods — differential tests and file forensics. The mentoring flipped: this story is his to teach now.
