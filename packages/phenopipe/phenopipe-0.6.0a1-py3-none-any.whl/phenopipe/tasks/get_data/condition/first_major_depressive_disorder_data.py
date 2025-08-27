from typing import List, Dict
from .icd_condition_data import IcdConditionData
from phenopipe.vocab.icds.conditions import MAJOR_DEPRESSIVE_DISORDER_ICDS


class FirstMajorDepressiveDisorderData(IcdConditionData):
    aggregate: str = "first"
    date_col: str = "first_major_depressive_disorder_entry_date"
    icd_codes: List[str] = MAJOR_DEPRESSIVE_DISORDER_ICDS
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
