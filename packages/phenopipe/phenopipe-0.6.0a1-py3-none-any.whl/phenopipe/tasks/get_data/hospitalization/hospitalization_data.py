from typing import List, Dict
from phenopipe.tasks.get_data.get_data import GetData
from phenopipe.tasks.task import completion
from phenopipe.query_builders import hospitalization_query


class HospitalizationData(GetData):
    hosp_codes: Dict[str, List[str]]

    cache_type: str = "std"

    @completion
    def complete(self):
        """
        Generic hospitalization condition occurance query phenotype
        """
        self.output = self.env_vars["query_conn"].get_query_rows(
            hospitalization_query(self.hosp_codes), return_df=True
        )

    def set_output_dtypes_and_names(self):
        self.output = self.output.rename(
            {"hospitalization_entry_date": self.date_col}
        ).select("person_id", self.date_col)
        self.set_date_column_dtype()
