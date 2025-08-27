from typing import List, Dict
from .icd_condition_data import IcdConditionData
from phenopipe.vocab.icds.conditions import ASTHMA_ICDS


class FirstAsthmaData(IcdConditionData):
    aggregate: str = "first"
    date_col: str = "first_asthma_entry_date"
    icd_codes: List[str] = ASTHMA_ICDS
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
