from typing import List, Dict
from .icd_condition_data import IcdConditionData
from phenopipe.vocab.icds.conditions import DEMENTIA_ICDS


class FirstDementiaData(IcdConditionData):
    aggregate: str = "first"
    date_col: str = "first_dementia_entry_date"
    icd_codes: List[str] = DEMENTIA_ICDS
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
