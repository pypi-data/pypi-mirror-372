from typing import List, Dict
from .icd_condition_data import IcdConditionData
from phenopipe.vocab.icds.conditions import COPD_EXACERBATION_ICDS


class FirstCopdExacerbationData(IcdConditionData):
    aggregate: str = "first"
    date_col: str = "first_copd_exacerbation_entry_date"
    icd_codes: List[str] = COPD_EXACERBATION_ICDS
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
