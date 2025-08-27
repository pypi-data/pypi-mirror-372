from typing import List, Dict
from .icd_condition_data import IcdConditionData
from phenopipe.vocab.icds.conditions import ACTINIC_KERATOSIS_ICDS


class FirstActinicKeratosisData(IcdConditionData):
    aggregate: str = "first"
    date_col: str = "first_actinic_keratosis_entry_date"
    icd_codes: List[str] = ACTINIC_KERATOSIS_ICDS
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
