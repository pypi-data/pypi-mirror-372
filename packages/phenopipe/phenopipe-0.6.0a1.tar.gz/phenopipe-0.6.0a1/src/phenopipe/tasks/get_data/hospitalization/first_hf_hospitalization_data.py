from typing import List, Dict
from .hospitalization_data import HospitalizationData
from phenopipe.vocab.icds.hospitalizations import HF_HOSPITALIZATION_CODES


class FirstHfHospitalizationData(HospitalizationData):
    aggregate: str = "first"
    date_col: str = "first_hf_hospitalization_entry_date"
    hosp_codes: Dict[str, List[str]] = HF_HOSPITALIZATION_CODES
