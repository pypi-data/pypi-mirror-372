from typing import List, Dict
from .icd_condition_data import IcdConditionData
from phenopipe.vocab.icds.conditions import HCM_ICDS


class FirstHcmData(IcdConditionData):
    aggregate: str = "first"
    date_col: str = "first_hcm_entry_date"
    icd_codes: List[str] = HCM_ICDS
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
