from typing import List, Dict
from .hospitalization_data import HospitalizationData
from phenopipe.vocab.icds.hospitalizations import HF_HOSPITALIZATION_CODES


class AllHfHospitalizationData(HospitalizationData):
    aggregate: str = "all"
    date_col: str = "hf_hospitalization_entry_date"
    hosp_codes: Dict[str, List[str]] = HF_HOSPITALIZATION_CODES
