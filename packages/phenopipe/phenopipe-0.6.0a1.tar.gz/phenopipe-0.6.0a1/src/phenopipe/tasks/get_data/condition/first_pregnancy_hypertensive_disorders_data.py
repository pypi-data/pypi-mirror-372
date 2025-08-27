from typing import List, Dict
from .icd_condition_data import IcdConditionData
from phenopipe.vocab.icds.conditions import PREGNANCY_HYPERTENSIVE_DISORDERS_ICDS


class FirstPregnancyHypertensiveDisordersData(IcdConditionData):
    aggregate: str = "first"
    date_col: str = "first_pregnancy_hypertensive_disorders_entry_date"
    icd_codes: List[str] = PREGNANCY_HYPERTENSIVE_DISORDERS_ICDS
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
