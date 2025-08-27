from typing import List, Dict
from .icd_condition_data import IcdConditionData
from phenopipe.vocab.icds.conditions import ISCHEMIC_STROKE_ICDS


class FirstIschemicStrokeData(IcdConditionData):
    aggregate: str = "first"
    date_col: str = "first_ischemic_stroke_entry_date"
    icd_codes: List[str] = ISCHEMIC_STROKE_ICDS
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
