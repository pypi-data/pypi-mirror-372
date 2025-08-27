from typing import List, Dict
from .icd_condition_data import IcdConditionData
from phenopipe.vocab.icds.conditions import INSOMNIA_ICDS


class FirstInsomniaData(IcdConditionData):
    aggregate: str = "first"
    date_col: str = "first_insomnia_entry_date"
    icd_codes: List[str] = INSOMNIA_ICDS
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
