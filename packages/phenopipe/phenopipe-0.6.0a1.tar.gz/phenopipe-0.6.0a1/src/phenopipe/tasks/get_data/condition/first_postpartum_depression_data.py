from typing import List, Dict
from .icd_condition_data import IcdConditionData
from phenopipe.vocab.icds.conditions import POSTPARTUM_DEPRESSION_ICDS


class FirstPostpartumDepressionData(IcdConditionData):
    aggregate: str = "first"
    date_col: str = "first_postpartum_depression_entry_date"
    icd_codes: List[str] = POSTPARTUM_DEPRESSION_ICDS
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
