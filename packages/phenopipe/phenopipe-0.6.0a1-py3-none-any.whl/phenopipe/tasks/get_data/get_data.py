from typing import Optional, TypeVar, Dict, List
from phenopipe.query_connections import BigQueryConnection
from phenopipe.tasks.task import Task
import warnings

PolarsDataFrame = TypeVar("polars.dataframe.frame.DataFrame")
PolarsLazyFrame = TypeVar("polars.lazyframe.frame.LazyFrame")


class GetData(Task):
    """
    Generic class to retrieve data from database.
    """

    #: bucket folder to save the output
    location: Optional[str] = "phenopipe_wd/datasets"

    large_query: bool = False

    #: either to check for cache in bucket
    cache: Optional[bool] = True

    #: either to check for cache in bucket
    cache_local: Optional[str] = ""

    #: cache type
    cache_type: Optional[str] = "bq"

    #: either to read or scan dataframe
    lazy: Optional[bool] = False

    state: Dict[str, List[str]] = {"aou": "untested", "std_omop": "untested"}

    def model_post_init(self, __context__=None):
        super().model_post_init()
        if self.env_vars.get("query_conn", None) is None:
            self.env_vars["query_conn"] = BigQueryConnection(
                lazy=self.lazy, cache=self.cache, verbose=not self.large_query
            )
        if self.large_query:
            self.cache_local = (
                f"{self.location}/{self.task_name}/{self.task_name}_*.csv"
            )
        else:
            self.cache_local = f"{self.location}/{self.task_name}.csv"

    def confirm_state(self):
        state = self.state[self.env_vars["query_conn"].query_platform]
        if state == "untested":
            warnings.warn(
                "This data task is not tested for this platform. Please be cautious that this query can throw errors or the resulting data may differ from intended query."
            )
        if state == "parsed":
            warnings.warn(
                "This data task is automatically parsed from another library. Please be cautious that this query can throw errors or the resulting data may differ from intended query."
            )
