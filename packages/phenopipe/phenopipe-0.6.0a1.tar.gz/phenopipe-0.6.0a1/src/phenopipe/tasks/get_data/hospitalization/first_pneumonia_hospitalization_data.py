from typing import List, Dict
from .hospitalization_data import HospitalizationData
from phenopipe.vocab.icds.conditions import PNEUMONIA_ICDS


class FirstPneumoniaHospitalizationData(HospitalizationData):
    aggregate: str = "first"
    date_col: str = "first_pneumonia_hospitalization_entry_date"
    hosp_codes: Dict[str, List[str]] = PNEUMONIA_ICDS
