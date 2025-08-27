from typing import List, Dict
from .lab_data import LabData
from phenopipe.vocab.terms.labs import HGBA1C_TERMS


class AllHgba1cData(LabData):
    date_col: str = "all_hgba1c_entry_date"
    val_col: str = "all_hgba1c_value"
    required_cols: List[str] = ["all_hgba1c_value"]
    lab_terms: List[str] = HGBA1C_TERMS
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
