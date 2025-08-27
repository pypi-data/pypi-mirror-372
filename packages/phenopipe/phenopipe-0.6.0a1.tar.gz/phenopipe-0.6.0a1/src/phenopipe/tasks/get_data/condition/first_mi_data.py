from typing import List, Dict
from .icd_condition_data import IcdConditionData
from phenopipe.vocab.icds.conditions import MI_ICDS


class FirstMiData(IcdConditionData):
    aggregate: str = "first"
    date_col: str = "first_mi_entry_date"
    icd_codes: List[str] = MI_ICDS
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
