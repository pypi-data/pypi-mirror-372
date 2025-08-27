from typing import List, Dict
from .lab_data import LabData
from phenopipe.vocab.terms.labs import TRIGS_TERMS


class AllTrigsData(LabData):
    date_col: str = "all_trigs_entry_date"
    val_col: str = "all_trigs_value"
    required_cols: List[str] = ["all_trigs_value"]
    lab_terms: List[str] = TRIGS_TERMS
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
