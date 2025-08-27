from typing import List, Dict
from .icd_condition_data import IcdConditionData
from phenopipe.vocab.icds.conditions import HFREF_ICDS


class FirstHfrefData(IcdConditionData):
    aggregate: str = "first"
    date_col: str = "first_hfref_entry_date"
    icd_codes: List[str] = HFREF_ICDS
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
