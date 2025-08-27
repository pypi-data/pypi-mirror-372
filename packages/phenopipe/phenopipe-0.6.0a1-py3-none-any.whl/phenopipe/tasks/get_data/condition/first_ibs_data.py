from typing import List, Dict
from .icd_condition_data import IcdConditionData
from phenopipe.vocab.icds.conditions import IBS_ICDS


class FirstIbsData(IcdConditionData):
    aggregate: str = "first"
    date_col: str = "first_ibs_entry_date"
    icd_codes: List[str] = IBS_ICDS
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
