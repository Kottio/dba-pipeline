{{ config(materialized='table') }}m
SELECT id as test_id, name, created_at FROM {{source('my_lake', 'test_table')}}