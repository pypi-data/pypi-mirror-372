from typing import List, Dict
from .icd_condition_data import IcdConditionData
from phenopipe.vocab.icds.conditions import GERD_ICDS


class FirstGerdData(IcdConditionData):
    aggregate: str = "first"
    date_col: str = "first_gerd_entry_date"
    icd_codes: List[str] = GERD_ICDS
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
