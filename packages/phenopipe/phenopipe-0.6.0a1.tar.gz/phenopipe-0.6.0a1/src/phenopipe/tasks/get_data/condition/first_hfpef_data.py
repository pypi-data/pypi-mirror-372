from typing import List, Dict
from .icd_condition_data import IcdConditionData
from phenopipe.vocab.icds.conditions import HFPEF_ICDS


class FirstHfpefData(IcdConditionData):
    aggregate: str = "first"
    date_col: str = "first_hfpef_entry_date"
    icd_codes: List[str] = HFPEF_ICDS
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
