from typing import List, Dict
from .icd_condition_data import IcdConditionData
from phenopipe.vocab.icds.conditions import GESTATIONAL_DIABETES_ICDS


class FirstGestationalDiabetesData(IcdConditionData):
    aggregate: str = "first"
    date_col: str = "first_gestational_diabetes_entry_date"
    icd_codes: List[str] = GESTATIONAL_DIABETES_ICDS
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
