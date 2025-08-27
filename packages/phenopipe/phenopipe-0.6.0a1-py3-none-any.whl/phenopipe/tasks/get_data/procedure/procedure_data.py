from typing import List
from phenopipe.tasks.get_data.get_data import GetData
from phenopipe.tasks.task import completion
from phenopipe.query_builders import cpt_procedure_query


class ProcedureData(GetData):
    cache_type: str = "std"
    procedure_codes: List[str]

    @completion
    def complete(self):
        """
        Generic procedure query phenotype
        """
        procedure_query_to_run = cpt_procedure_query(self.procedure_codes)
        self.output = self.env_vars["query_conn"].get_query_rows(
            procedure_query_to_run, return_df=True
        )

    def set_output_dtypes_and_names(self):
        self.output = self.output.rename({"entry_date": self.date_col}).select(
            "person_id", self.date_col
        )
        self.set_date_column_dtype()
