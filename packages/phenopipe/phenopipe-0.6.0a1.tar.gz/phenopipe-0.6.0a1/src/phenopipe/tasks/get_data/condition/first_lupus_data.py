from typing import List, Dict
from .icd_condition_data import IcdConditionData
from phenopipe.vocab.icds.conditions import LUPUS_ICDS


class FirstLupusData(IcdConditionData):
    aggregate: str = "first"
    date_col: str = "first_lupus_entry_date"
    icd_codes: List[str] = LUPUS_ICDS
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
