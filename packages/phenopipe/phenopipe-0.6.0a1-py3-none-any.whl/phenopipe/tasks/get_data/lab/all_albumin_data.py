from typing import List, Dict
from .lab_data import LabData
from phenopipe.vocab.terms.labs import ALBUMIN_TERMS


class AllAlbuminData(LabData):
    date_col: str = "all_albumin_entry_date"
    lab_terms: Dict[str, List[str]] = ALBUMIN_TERMS
    val_col: str = "all_albumin_value"
    required_cols: List[str] = ["all_albumin_value"]
