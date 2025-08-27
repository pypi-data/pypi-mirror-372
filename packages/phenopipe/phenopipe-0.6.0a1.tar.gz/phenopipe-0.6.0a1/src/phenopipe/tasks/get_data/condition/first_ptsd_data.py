from typing import List, Dict
from .icd_condition_data import IcdConditionData
from phenopipe.vocab.icds.conditions import PTSD_ICDS


class FirstPtsdData(IcdConditionData):
    aggregate: str = "first"
    date_col: str = "first_ptsd_entry_date"
    icd_codes: List[str] = PTSD_ICDS
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
