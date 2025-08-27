from typing import List, Dict
from .lab_data import LabData
from phenopipe.vocab.terms.labs import CHOLESTEROL_TERMS


class AllCholesterolData(LabData):
    date_col: str = "all_cholesterol_entry_date"
    val_col: str = "all_cholesterol_value"
    required_cols: List[str] = ["all_cholesterol_value"]
    lab_terms: List[str] = CHOLESTEROL_TERMS
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
