# CLAUDE.md — AI operating manual for this repo

You are working on **DBuilders Pipeline**: a self-hosted analytics platform (course-platform Postgres → dlt → DuckLake → dbt → Dagster → Evidence + MCP) on a Digital Ocean VPS. It is a public demo project for Analytics Engineering students — code quality and clarity matter as much as functionality.

## Ground rules

1. **Never invent data.** Before writing or modifying a model, preview the real source data. Never fabricate `accepted_values`, column names, or example values — check them against the warehouse.
2. **Validate after building.** After creating/changing a model, run it and run its tests. A task is not done until `dbt build --select <model>+` is green.
3. **No secrets in code.** Credentials come from `.env` (never committed) or the server environment. If you need a new variable, add it to `.env.example` with a placeholder.
4. **PII is pseudonymized at ingestion.** Never propagate raw emails/names downstream; staging models select from already-safe raw tables.
5. **Small, reviewable changes.** One concern per PR. Write PR descriptions a student could learn from: what, why, how verified.

## Conventions

- Python: managed with `uv`; lint with `ruff` (config in `pyproject.toml`). Type hints on public functions.
- SQL/dbt: `stg_` / `int_` / `fct_` / `dim_` / `mart_` prefixes; one model per file; CTEs over subqueries; `sqlfluff` (dialect: duckdb) must pass.
- dbt layers: `staging` = 1:1 with sources, rename + cast only · `intermediate` = reusable logic · `marts` = business-facing, documented, tested.
- Every mart model: description, column docs, at least unique + not_null on its key, an explicit `meta: owner`.
- Commits: Conventional Commits (`feat:`, `fix:`, `docs:`, `refactor:`, `ci:`, `infra:`).
- Decisions with alternatives → short ADR in `docs/decisions/` (copy the format of 0001).

## Commands

_(filled in as phases land)_

- Env: `uv sync`
- Lint: `uv run ruff check . && uv run sqlfluff lint transform/`
- dbt: `cd transform && dbt build` (targets: `dev` local, `prod` on VPS)
- Local services: `docker compose -f infra/docker-compose.yml up -d`

## Documentation workflow (who writes what)

- **`Notes/Notetaking.md`** (gitignored): Tom's raw personal notes, any language, any mess. AI never writes here.
- **`Notes/Cleaned_Notes.md`** (gitignored): when Tom says *"look at notetaking"*, the AI tidies the new raw notes into here — same content, same voice, same language (FR stays FR), typos fixed, commands as code blocks. For Tom to re-read the steps. No AI additions.
- **`docs/ai-log.md`**: from those same notes + the session, the AI appends the honest working-with-AI record — one entry per work session: task given, what AI did well, what the human had to correct, lesson. Failures are the valuable part.
- **`docs/decisions/`** (ADRs): any decision with real alternatives (engine, storage, ordering). AI drafts, numbered sequentially; Tom reviews, edits, commits. A decision isn't taken until Tom says so.
- **`docs/build-plan.md`**: the living plan. The **"📍 Next step"** block at the top is the re-entry point — the AI refreshes it when Tom ends a session ("call it a day").

## Working rules with the owner

- **Git belongs to Tom.** The AI never runs `git init/add/commit/push` — it proposes commands and file contents; Tom executes and commits.
- **Organic growth.** No file, dependency, or config enters the repo before the phase that needs it, and nothing enters that Tom can't explain. Explain first, create after agreement.
- **Decisions on evidence, not AI assumptions.** When the AI is unsure (beta tools, current versions), say so and propose a small test; Tom's 10-minute test beats training data.

## When unsure

Prefer asking / leaving a `TODO(question):` comment over guessing business logic. Grain decisions, metric definitions, and PII classification are human calls — flag them, don't decide them.


