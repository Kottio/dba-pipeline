
  
    
    
    create  table
      "my_ducklake"."main"."stg_test_table__dbt_tmp"
  
    as (
      
SELECT id as test_id, name, created_at FROM "my_ducklake"."my_lake"."test_table"
    );
  
    
  