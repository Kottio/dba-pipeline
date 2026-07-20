{{ config(materialized='table') }}
SELECT id as test_id, name, created_at FROM {{source('my_lake', 'test_table')}}