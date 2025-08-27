from typing import List
from phenopipe.tasks.get_data.get_data import GetData
from phenopipe.tasks.task import completion
from phenopipe.query_builders import lab_query


class LabData(GetData):
    #: if query is large according to google cloud api
    lab_terms: List[str]

    @completion
    def complete(self):
        """
        Generic lab query phenotype
        """
        lab_query_to_run = lab_query(**self.lab_terms)
        self.output = self.env_vars["query_conn"].get_query_df(
            lab_query_to_run, self.task_name, self.lazy, self.cache, self.cache_local
        )

    def set_output_dtypes_and_names(self):
        self.output = self.output.rename(
            {
                "measurement_date": self.date_col,
                "value_as_number": self.val_col,
                "unit_source_value": f"{self.val_col}_unit",
            }
        )
        self.set_date_column_dtype()
