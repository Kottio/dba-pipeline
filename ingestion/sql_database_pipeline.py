# flake8: noqa
import humanize
from typing import Any

import dlt
from dlt.common import pendulum
from dlt.sources.credentials import ConnectionStringCredentials
from dlt.sources.sql_database import sql_database, sql_table, Table

def load_select_tables_from_database() -> None:
    """Use the sql_database source to reflect an entire database schema and load select tables from it.

    This example sources data from the public Rfam MySQL database.
    """
    # Create a pipeline
    pipeline = dlt.pipeline(pipeline_name="dba_ingest", destination='ducklake', dataset_name="raw")
    source_1 = sql_database().with_resources("students")

    # Add incremental config to the resources. "updated" is a timestamp column in these tables that gets used as a cursor
    source_1.students.apply_hints(incremental=dlt.sources.incremental("updated_at"))


    # Run the pipeline. The merge write disposition merges existing rows in the destination by primary key
    info = pipeline.run(source_1, write_disposition="merge")
    print(info)

    # Load some other tables with replace write disposition. This overwrites the existing tables in destination
    # source_2 = sql_database(credentials).with_resources("features", "author")
    # info = pipeline.run(source_2, write_disposition="replace")
    # print(info)

    # Load a table incrementally with append write disposition
    # this is good when a table only has new rows inserted, but not updated
    # source_3 = sql_database(credentials).with_resources("genome")
    # source_3.genome.apply_hints(incremental=dlt.sources.incremental("created"))

    info = pipeline.run(source_1, write_disposition="append")
    print(info)



def load_standalone_table_resource() -> None:
    """Load a few known tables with the standalone sql_table resource, request full schema and deferred
    table reflection"""
    pipeline = dlt.pipeline(
        pipeline_name="dba_pipeline",
        destination='ducklake',
        dataset_name="lake_schema",
        dev_mode=True,
    )

    # Load a table incrementally starting at a given date
    # Adding incremental via argument like this makes extraction more efficient
    # as only rows newer than the start date are fetched from the table
    # we also use `detect_precision_hints` to get detailed column schema
    # and defer_table_reflect to reflect schema only during execution
    family = sql_table(
        credentials=ConnectionStringCredentials(
            "mysql+pymysql://rfamro@mysql-rfam-public.ebi.ac.uk:4497/Rfam"
        ),
        table="family",
        incremental=dlt.sources.incremental(
            "updated",
        ),
        reflection_level="full_with_precision",
        defer_table_reflect=True,
    )
    # columns will be empty here due to defer_table_reflect set to True
    print(family.compute_table_schema())

    # Load all data from another table
    genome = sql_table(
        credentials="mysql+pymysql://rfamro@mysql-rfam-public.ebi.ac.uk:4497/Rfam",
        table="genome",
        reflection_level="full_with_precision",
        defer_table_reflect=True,
    )

    # Run the resources together (just take one page of results to make it faster)
    info = pipeline.extract([family.add_limit(1), genome.add_limit(1)], write_disposition="merge")
    print(info)
    # Show inferred columns
    print(pipeline.default_schema.to_pretty_yaml())






if __name__ == "__main__":
    # Load selected tables with different settings
    load_select_tables_from_database()

    # load_entire_database()
    # select_with_end_value_and_row_order()

    # Load tables with the standalone table resource
    # load_standalone_table_resource()

    # Load all tables from the database.
    # Warning: The sample database is very large
    # load_entire_database()
