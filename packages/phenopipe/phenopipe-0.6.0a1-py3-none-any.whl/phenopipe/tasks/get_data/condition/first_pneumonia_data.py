from typing import List
from .icd_condition_data import IcdConditionData
from phenopipe.vocab.icds.conditions import PNEUMONIA_ICDS


class FirstPneumoniaData(IcdConditionData):
    aggregate: str = "first"
    date_col: str = "first_pneumonia_entry_date"
    icd_codes: List[str] = PNEUMONIA_ICDS
