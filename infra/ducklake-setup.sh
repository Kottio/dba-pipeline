#!/usr/bin/env bash
set -euo pipefail   # stop on any error

# Birth certificate of the lake. Idempotent — safe to re-run.
# RULE: DATA_PATH is recorded VERBATIM at creation; we declare it ABSOLUTE ($(pwd))
# so every client (dlt, dbt, CLI) can announce the identical string. (See Knowledge Center note.)

mkdir -p data

duckdb -c "INSTALL ducklake;"
duckdb -c "ATTACH 'ducklake:data/lake_catalog.ducklake' AS lake (DATA_PATH '$(pwd)/data/lake_files/');"

echo "Lake ready:"
duckdb data/lake_catalog.ducklake -c "SELECT key, value FROM ducklake_metadata WHERE key='data_path';"
