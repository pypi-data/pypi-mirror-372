from typing import List, Dict
from .icd_condition_data import IcdConditionData
from phenopipe.vocab.icds.conditions import HYPERLIPIDEMIA_ICDS


class FirstHyperlipidemiaData(IcdConditionData):
    aggregate: str = "first"
    date_col: str = "first_hyperlipidemia_entry_date"
    icd_codes: List[str] = HYPERLIPIDEMIA_ICDS
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
