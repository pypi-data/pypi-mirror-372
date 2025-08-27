from typing import List, Dict
from .hospitalization_data import HospitalizationData
from phenopipe.vocab.icds.conditions import MI_ICDS


class AllMiHospitalizationData(HospitalizationData):
    aggregate: str = "all"
    date_col: str = "mi_hospitalization_entry_date"
    hosp_codes: Dict[str, List[str]] = MI_ICDS
