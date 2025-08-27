from typing import List, Dict
from .icd_condition_data import IcdConditionData
from phenopipe.vocab.icds.conditions import IBD_ICDS


class FirstIbdData(IcdConditionData):
    aggregate: str = "first"
    date_col: str = "first_ibd_entry_date"
    icd_codes: List[str] = IBD_ICDS
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
