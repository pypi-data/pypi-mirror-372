from typing import List, Dict
from .icd_condition_data import IcdConditionData
from phenopipe.vocab.icds.conditions import DIABETIC_KETOACIDOSIS_ICDS


class FirstDiabeticKetoacidosisData(IcdConditionData):
    aggregate: str = "first"
    date_col: str = "first_diabetic_ketoacidosis_entry_date"
    icd_codes: List[str] = DIABETIC_KETOACIDOSIS_ICDS
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
