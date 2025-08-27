from typing import List, Dict, Any
import polars as pl
from phenopipe.tasks.get_data.get_data import GetData
from phenopipe.tasks.task import completion
from phenopipe.query_builders import sleep_level_query


class SleepLevelsData(GetData):
    large_query: bool = True
    sleep_levels: List[str]
    sql_aggregation: str = "all"
    is_main_sleep: bool = False
    min_output_schema: Dict[str, Any] = {
        "person_id": pl.Int64,
        "is_main_sleep": pl.Boolean,
        "sleep_date": pl.Date,
        "sleep_datetime": pl.Datetime,
        "sleep_level": pl.String,
    }

    @completion
    def complete(self):
        """
        Generic icd condition occurance query phenotype
        """
        sleep_query_to_run = sleep_level_query(
            self.sleep_levels, self.sql_aggregation, self.is_main_sleep
        )
        self.output = self.env_vars["query_conn"].get_query_df(
            sleep_query_to_run, self.task_name, self.lazy, self.cache, self.cache_local
        )
