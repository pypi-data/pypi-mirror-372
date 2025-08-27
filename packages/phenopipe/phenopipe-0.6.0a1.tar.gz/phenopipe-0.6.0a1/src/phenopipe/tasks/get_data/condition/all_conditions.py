from typing import List, Dict
from .icd_condition_data import IcdConditionData


class AllConditionsData(IcdConditionData):
    large_query: bool = True
    date_col: str = "condition_start_entry_date"
    icd_codes: Dict[str, List[str]] = None

    def set_output_dtypes_and_names(self):
        self.output.rename({"condition_start_date": self.date_col})
        self.set_date_column_dtype()
