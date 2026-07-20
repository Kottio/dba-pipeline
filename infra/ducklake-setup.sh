mkdir data
duckdb -c "INSTALL ducklake;"
duckdb -c "ATTACH 'ducklake:data/lake_catalog.ducklake' AS datalake (DATA_PATH 'data/lake_files/');"
