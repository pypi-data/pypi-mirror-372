from typing import List, Dict
from .lab_data import LabData
from phenopipe.vocab.terms.labs import SODIUM_TERMS


class AllSodiumData(LabData):
    date_col: str = "all_sodium_entry_date"
    val_col: str = "all_sodium_value"
    required_cols: List[str] = ["all_sodium_value"]
    lab_terms: List[str] = SODIUM_TERMS
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
