import os
from typing import TypeVar, Optional, Callable
import polars as pl
from databricks.connect import DatabricksSession
from pydantic import PrivateAttr
from .query_connection import QueryConnection

PolarsDataFrame = TypeVar("polars.dataframe.frame.DataFrame")
PolarsLazyFrame = TypeVar("polars.lazyframe.frame.LazyFrame")


class DatabricksQueryConnection(QueryConnection):
    #: databricks cluster name
    cluster_id: Optional[str] = os.getenv("DATABRICKS_CLUSTER")

    #: databricks host
    host: Optional[str] = os.getenv("DATABRICKS_HOST")

    #: databricks token
    _token: Optional[str] = PrivateAttr(os.getenv("DATABRICKS_TOKEN"))

    # defult databricks catalog
    default_catalog: Optional[str] = os.getenv("DATABRICKS_DEFAULT_CATALOG")

    # defult databricks catalog
    default_database: Optional[str] = os.getenv("DATABRICKS_DEFAULT_DATABASE")

    #: function to check cache availability
    cache_ls_func: Optional[Callable] = lambda x: None

    #: function to cache data
    cache_read_func: Optional[Callable] = lambda x: None

    #: function to cache data
    cache_write_func: Optional[Callable] = lambda x, y: None

    # limit the query rows
    limit: Optional[int] = -1

    query_platform: str = "std_omop"

    def get_cache(self, local: str, client=None, lazy: Optional[bool] = False):
        return None

    def get_query_df(self, query: str, *args, **kwargs) -> pl.DataFrame:
        """
        Runs the given query on databricks remote connection and returns the output as polars dataframe
        :param query: Query string to on databricks
        """
        res = self.get_query_rows(query, return_df=False)
        if self.limit != -1:
            res = res.limit(self.limit)
        return pl.from_pandas(res.toPandas())

    def get_query_rows(
        self, query: str, return_df: bool = False, *args, **kwargs
    ) -> pl.DataFrame:
        """
        Runs the given query on databricks remote connection and returns the output as polars dataframe
        :param query: Query string to on databricks
        """
        spark = DatabricksSession.builder.remote(
            host=self.host, token=self._token, cluster_id=self.cluster_id
        ).getOrCreate()
        spark.catalog.setCurrentCatalog(self.default_catalog)
        spark.catalog.setCurrentDatabase(self.default_database)
        res = spark.sql(query)
        if self.limit != -1:
            res = res.limit(self.limit)
        if return_df:
            return pl.from_pandas(res.toPandas())
        else:
            return res
