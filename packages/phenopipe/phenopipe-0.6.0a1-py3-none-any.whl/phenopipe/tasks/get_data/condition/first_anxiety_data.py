from typing import List, Dict
from .icd_condition_data import IcdConditionData
from phenopipe.vocab.icds.conditions import ANXIETY_ICDS


class FirstAnxietyData(IcdConditionData):
    aggregate: str = "first"
    date_col: str = "first_anxiety_entry_date"
    icd_codes: List[str] = ANXIETY_ICDS
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
