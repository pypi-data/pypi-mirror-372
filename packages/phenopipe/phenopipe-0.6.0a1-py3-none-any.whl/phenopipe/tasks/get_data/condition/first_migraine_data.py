from typing import List, Dict
from .icd_condition_data import IcdConditionData
from phenopipe.vocab.icds.conditions import MIGRAINE_ICDS


class FirstMigraineData(IcdConditionData):
    aggregate: str = "first"
    date_col: str = "first_migraine_entry_date"
    icd_codes: List[str] = MIGRAINE_ICDS
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
