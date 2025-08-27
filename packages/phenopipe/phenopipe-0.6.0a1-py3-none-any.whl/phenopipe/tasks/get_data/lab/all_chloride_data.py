from typing import List, Dict
from .lab_data import LabData
from phenopipe.vocab.terms.labs import CHLORIDE_TERMS


class AllChlorideData(LabData):
    date_col: str = "all_chloride_entry_date"
    val_col: str = "all_chloride_value"
    required_cols: List[str] = ["all_chloride_value"]
    lab_terms: List[str] = CHLORIDE_TERMS
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
