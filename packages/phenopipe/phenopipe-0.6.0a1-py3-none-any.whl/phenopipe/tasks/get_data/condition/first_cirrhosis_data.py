from typing import List, Dict
from .icd_condition_data import IcdConditionData
from phenopipe.vocab.icds.conditions import CIRRHOSIS_ICDS


class FirstCirrhosisData(IcdConditionData):
    aggregate: str = "first"
    date_col: str = "first_cirrhosis_entry_date"
    icd_codes: List[str] = CIRRHOSIS_ICDS
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
