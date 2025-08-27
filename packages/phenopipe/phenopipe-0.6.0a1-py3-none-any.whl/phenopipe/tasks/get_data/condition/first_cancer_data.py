from typing import List, Dict
from .icd_condition_data import IcdConditionData
from phenopipe.vocab.icds.conditions import CANCER_ICDS


class FirstCancerData(IcdConditionData):
    aggregate: str = "first"
    date_col: str = "first_cancer_entry_date"
    icd_codes: List[str] = CANCER_ICDS
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
