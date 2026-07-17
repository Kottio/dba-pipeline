# ingestion/ — Phase 2

dlt pipelines: prod course-platform Postgres → DuckLake `raw` schema.
Incremental where a cursor exists, PII pseudonymized at the door.
Ingestion contracts (owner, cursor, PII columns, freshness) live in `docs/contracts/`.
