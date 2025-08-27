from typing import List, Dict
from .icd_condition_data import IcdConditionData
from phenopipe.vocab.icds.conditions import POTS_ICDS


class FirstPotsData(IcdConditionData):
    aggregate: str = "first"
    date_col: str = "first_pots_entry_date"
    icd_codes: List[str] = POTS_ICDS
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
