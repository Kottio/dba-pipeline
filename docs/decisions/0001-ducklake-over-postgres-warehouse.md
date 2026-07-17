# ADR 0001 — DuckDB + DuckLake (Postgres catalog) over Postgres-as-warehouse

**Status:** accepted · 2026-07-17

## Context

Source data (course platform) lives in a small production Postgres. The analytical store must run cheaply on a Digital Ocean VPS, be queried concurrently by Dagster (writes), Evidence and an MCP server (reads), and serve as a **teaching artifact** for AE students. Data volume is small — pure performance is *not* the deciding factor.

Options considered: (a) second Postgres database as warehouse, (b) DuckDB single-file, (c) DuckDB + DuckLake with a Postgres catalog, (d) ClickHouse, (e) MotherDuck.

## Decision

**DuckDB + DuckLake, with the catalog in a dedicated Postgres.**

## Rationale

1. **Teaching value.** Postgres→Postgres teaches nothing about warehouses. DuckLake gives columnar execution, storage/compute separation, an open table format, snapshots/time travel — every Snowflake/BigQuery concept, visible as files you can `ls` on a server.
2. **Concurrency.** A single `.duckdb` file is effectively single-writer — awkward with Dagster writing while Evidence/MCP read. DuckLake is designed for concurrent multi-client access; this removes the main argument for plain Postgres.
3. **Postgres isn't rejected — it's recruited.** DuckLake's catalog runs in Postgres, so the stack still demonstrates Postgres operations, one step removed from prod.
4. **Cost & self-hosting.** ~€0 software cost, fits the one-person-on-a-VPS thesis. ClickHouse: too much ops for the need. MotherDuck: managed, weakens the self-hosted story.

## Consequences

- (+) Lakehouse concepts demonstrable in miniature; backup is file copy + catalog dump.
- (−) DuckLake is young — expect rough edges; document them (that's content, not failure).
- (−) One more moving part than pure Postgres (catalog service in compose).
- Revisit if: volumes explode (→ MotherDuck) or the project needs real-time (→ ClickHouse).
