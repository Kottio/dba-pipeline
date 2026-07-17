# transform/ — Phase 3

dbt project (dbt-duckdb, attached to DuckLake).
Layers: `staging` (1:1, rename/cast) → `intermediate` → `marts` (documented, tested, owned).
Design first: the ERD + grain decisions are PR'd as a doc before model #1.
