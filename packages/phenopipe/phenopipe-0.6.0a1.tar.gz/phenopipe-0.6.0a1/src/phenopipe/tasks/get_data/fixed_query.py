from phenopipe.tasks.get_data.get_data import GetData
from phenopipe.tasks.task import completion


class FixedQuery(GetData):
    query: str

    @completion
    def complete(self):
        """
        Query a fixed sql query from fixed queries vocabulary and update self.output with resulting dataframe
        """
        self.output = self.env_vars["query_conn"].get_query_df(
            self.query, self.task_name, self.lazy, self.cache, self.cache_local
        )

    def set_output_dtypes_and_names(self):
        self.set_date_column_dtype(self.date_col)
