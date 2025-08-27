from typing import List
from phenopipe.tasks.get_data.get_data import GetData
from phenopipe.tasks.task import completion
from phenopipe.query_builders import med_query


class MedicationData(GetData):
    #: if query is large according to google cloud api
    med_terms: List[str]

    @completion
    def complete(self):
        """
        Generic medication query phenotype
        """
        med_query_to_run = med_query(self.med_terms)
        self.output = self.env_vars["query_conn"].get_query_df(
            med_query_to_run, self.task_name, self.lazy, self.cache, self.cache_local
        )

    def set_output_dtypes_and_names(self):
        self.output = self.output.rename(
            {"drug_exposure_start_date": self.date_col}
        ).select("person_id", self.date_col)
        self.set_date_column_dtype()
