# DBuilders Pipeline — every operation the project supports, as named recipes.
# `just` alone lists them. Recipes always run from the repo root, with .env loaded.
set dotenv-load

# Birth the lake (idempotent; absolute DATA_PATH — see infra/ducklake-setup.sh)
init-lake:
    ./infra/ducklake-setup.sh

# Open a SQL session on the lake (close it before running pipelines — file lock!)
lakehouse:
    duckdb -cmd "ATTACH 'ducklake:$LAKE_CATALOG' AS lake; USE lake;"

# List everything in the lake
tables:
    duckdb -c "ATTACH 'ducklake:$LAKE_CATALOG' AS lake; SHOW ALL TABLES;"

# X-ray the catalog's bookkeeping (recorded data_path etc.)
xray:
    duckdb $LAKE_CATALOG -c "SELECT key, value FROM ducklake_metadata;"

# --- coming with their phases (organic rule) ---
# ingest:      uv run python ingestion/pipeline.py
# transform:   dbt run --project-dir transform
