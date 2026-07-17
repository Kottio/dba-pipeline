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

## When unsure

Prefer asking / leaving a `TODO(question):` comment over guessing business logic. Grain decisions, metric definitions, and PII classification are human calls — flag them, don't decide them.
