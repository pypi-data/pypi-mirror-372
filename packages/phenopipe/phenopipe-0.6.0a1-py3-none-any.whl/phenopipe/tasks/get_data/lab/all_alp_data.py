from typing import List, Dict
from .lab_data import LabData
from phenopipe.vocab.terms.labs import ALP_TERMS


class AllAlpData(LabData):
    date_col: str = "all_alp_entry_date"
    val_col: str = "all_alp_value"
    required_cols: List[str] = ["all_alp_value"]
    lab_terms: List[str] = ALP_TERMS
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
