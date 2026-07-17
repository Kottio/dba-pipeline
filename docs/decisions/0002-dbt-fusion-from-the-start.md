# ADR 0002 — dbt Fusion engine from the start (not dbt Core)

**Status:** accepted · 2026-07-17

## Context

The transform layer was planned on dbt Core (`dbt-duckdb`, Python). dbt Fusion — the new
Rust engine — now ships a DuckDB adapter (Beta, Fusion CLI only). Fusion is where dbt is
heading, and nobody is teaching a Fusion + DuckDB + DuckLake stack yet.

## Decision

Build on **dbt Fusion from day one**. Version pinned: `2.0.0-preview.196`
(updates applied deliberately, never reflexively — beta moves fast).

## Proof

Tested locally before deciding: `dbt debug` against a DuckLake catalog
(`adapter: duckdb`, path `my_ducklake.ducklake`) — all checks passed, 883ms.

## Consequences

- (+) Current-generation engine; faster parse/compile; strong content angle (Fusion tutorial is in the idea pool).
- (−) Beta: expect rough edges; each one gets documented (ai-log / ADRs), not worked around silently.
- (−) dbt no longer travels via `pyproject.toml`/uv — it is a binary. Recipe = pinned version in README prerequisites (and a Dockerfile line when prod comes).
- (?) `dagster-dbt` integration untested against Fusion — verify at the orchestration phase; fallback is Dagster invoking the Fusion CLI directly.
- **Escape hatch:** dbt projects remain compatible with dbt Core — reverting to `dbt-duckdb` stays possible at any time.
