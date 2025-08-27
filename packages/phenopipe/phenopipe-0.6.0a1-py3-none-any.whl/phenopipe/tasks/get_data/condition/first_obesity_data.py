from typing import List
from .icd_condition_data import IcdConditionData
from phenopipe.vocab.icds.conditions import OBESITY_ICDS


class FirstObesityData(IcdConditionData):
    aggregate: str = "first"
    date_col: str = "first_obesity_entry_date"
    icd_codes: List[str] = OBESITY_ICDS
