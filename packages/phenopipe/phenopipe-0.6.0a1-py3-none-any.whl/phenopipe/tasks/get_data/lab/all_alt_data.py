from typing import List, Dict
from .lab_data import LabData
from phenopipe.vocab.terms.labs import ALT_TERMS


class AllAltData(LabData):
    date_col: str = "all_alt_entry_date"
    val_col: str = "all_alt_value"
    required_cols: List[str] = ["all_alt_value"]
    lab_terms: List[str] = ALT_TERMS
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
