from typing import List, Dict
from .hospitalization_data import HospitalizationData
from phenopipe.vocab.icds.conditions import COPD_ICDS


class FirstCopdHospitalizationData(HospitalizationData):
    aggregate: str = "first"
    date_col: str = "first_copd_hospitalization_entry_date"
    hosp_codes: Dict[str, List[str]] = COPD_ICDS
