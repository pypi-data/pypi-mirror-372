import os
from typing import Optional, Callable
from subprocess import CalledProcessError
from google.cloud.bigquery import Client
from google.cloud import bigquery
import polars as pl
import warnings
from phenopipe.bucket import ls_bucket, read_csv_from_bucket, write_csv_to_bucket
from .query_connection import QueryConnection

# data type mapping between big query tables and polars. not intended to be full list only to cover most recent aou dataset.
BQ_DATA_MAPPING = {
    "STRING": pl.String,
    "FLOAT64": pl.Float64,
    "FLOAT32": pl.Float32,
    "INT8": pl.Int8,
    "INT16": pl.Int16,
    "INT32": pl.Int32,
    "INT64": pl.Int64,
    "INT128": pl.Int128,
    "TIMESTAMP": pl.Datetime(),
    "DATETIME": pl.Datetime(),
    "DATE": pl.Date,
    "BOOL": pl.Boolean,
    "NUMERIC": pl.Float64,
    "ARRAY<INT64>": pl.List(pl.Int64),
    "ARRAY<STRING>": pl.List(pl.String),
}


class BigQueryConnection(QueryConnection):
    #: bucket id to save the result
    bucket_id: Optional[str] = os.getenv("WORKSPACE_BUCKET")

    #: default dataset
    default_dataset: Optional[str] = os.getenv("WORKSPACE_CDR")

    #: function to check cache availability
    cache_ls_func: Optional[Callable] = ls_bucket

    #: function to cache data
    cache_read_func: Optional[Callable] = read_csv_from_bucket

    #: function to cache data
    cache_write_func: Optional[Callable] = write_csv_to_bucket

    #: either to run caching verbose
    verbose: bool = True

    query_platform: str = "aou"

    def get_cache(
        self, local: str, client: Optional[Client] = None, lazy: Optional[bool] = False
    ):
        if client is None:
            client = Client()
        try:
            self.cache_ls_func(local, return_list=True)
            return self.cache_read_func(local, lazy=lazy, verbose=self.verbose)
        except CalledProcessError:
            return None

    def get_query_rows(
        self, query: str, return_df: bool = False, client: Optional[Client] = None
    ):
        """
        Runs the given query and returns the client and bigquery iterator
        :param query: Query string to run with google big query.
        """
        if client is None:
            client = Client()
        res = client.query_and_wait(
            query,
            job_config=bigquery.job.QueryJobConfig(
                default_dataset=self.default_dataset
            ),
        )
        if not return_df:
            return res
        else:
            return pl.from_arrow(res.to_arrow())

    def get_query_df(
        self,
        query: str,
        query_name: str,
        lazy: Optional[bool] = False,
        cache: Optional[bool] = False,
        cache_local: Optional[str] = None,
    ) -> pl.DataFrame:
        """
        Runs the given query and saves the resulting dataframe to the given bucket and location and returns the dataframe
        :param query: Query string to run with google big query.
        """

        if cache and cache_local is None:
            raise ValueError("No cache location is given!")

        client = Client()
        res = self.get_query_rows(query=query, return_df=False, client=client)
        print(f"{query_name} is ran!")
        if cache or cache is None:
            if res._table:
                ex_res = client.extract_table(
                    res._table, f"{self.bucket_id}/{cache_local}"
                )
                if ex_res.result().done():
                    print(f"Given query is successfully saved into {cache_local}")
            else:
                self.cache_write_func(pl.from_arrow(res.to_arrow()), cache_local)
                warnings.warn(
                    f"Query didn't return any table. Given result is saved into {cache_local}"
                )
        if not lazy:
            return pl.from_arrow(res.to_arrow())
        else:
            return pl.from_arrow(res.to_arrow()).lazy()

    def get_table_names(self):
        """
        Get table names from the default dataset
        """
        query = """SELECT table_name FROM `INFORMATION_SCHEMA.TABLES`;"""
        tables = self.get_query_rows(query)
        return list(map(lambda x: x.get("table_name"), tables))

    def get_table_schema(self, table: str):
        """
        Gets te column names and datatypes of the given table
        :param table: Table name to get columns from
        """
        query = """SELECT * FROM `INFORMATION_SCHEMA.COLUMNS`;"""
        columns = self.get_query_rows(query)
        return pl.Schema(
            {
                col.get("column_name"): BQ_DATA_MAPPING[col.get("data_type")]
                for col in columns
                if col.get("table_name") == table
            }
        )
