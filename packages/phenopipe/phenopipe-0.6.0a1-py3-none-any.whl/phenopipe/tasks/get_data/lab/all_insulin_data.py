from typing import List, Dict
from .lab_data import LabData
from phenopipe.vocab.terms.labs import INSULIN_TERMS


class AllInsulinData(LabData):
    date_col: str = "all_insulin_entry_date"
    val_col: str = "all_insulin_value"
    required_cols: List[str] = ["all_insulin_value"]
    lab_terms: List[str] = INSULIN_TERMS
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
