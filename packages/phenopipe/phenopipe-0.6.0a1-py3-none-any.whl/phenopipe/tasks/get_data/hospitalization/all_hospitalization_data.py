from typing import List, Dict
from .hospitalization_data import HospitalizationData


class AllHospitalizationData(HospitalizationData):
    date_col: str = "hospitalization_entry_date"
    hosp_codes: Dict[str, List[str]] = None

    def set_output_dtypes_and_names(self):
        self.set_date_column_dtype()
