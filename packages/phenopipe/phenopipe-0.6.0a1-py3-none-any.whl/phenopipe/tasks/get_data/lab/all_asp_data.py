from typing import List, Dict
from .lab_data import LabData
from phenopipe.vocab.terms.labs import ASP_TERMS


class AllAspData(LabData):
    date_col: str = "all_asp_entry_date"
    val_col: str = "all_asp_value"
    required_cols: List[str] = ["all_asp_value"]
    lab_terms: List[str] = ASP_TERMS
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
