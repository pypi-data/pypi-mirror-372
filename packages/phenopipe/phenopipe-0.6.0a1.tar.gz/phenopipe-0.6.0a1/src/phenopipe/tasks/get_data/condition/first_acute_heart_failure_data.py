from typing import List, Dict
from .icd_condition_data import IcdConditionData
from phenopipe.vocab.icds.conditions import ACUTE_HEART_FAILURE_ICDS


class FirstAcuteHeartFailureData(IcdConditionData):
    aggregate: str = "first"
    date_col: str = "first_acute_heart_failure_entry_date"
    icd_codes: List[str] = ACUTE_HEART_FAILURE_ICDS
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
