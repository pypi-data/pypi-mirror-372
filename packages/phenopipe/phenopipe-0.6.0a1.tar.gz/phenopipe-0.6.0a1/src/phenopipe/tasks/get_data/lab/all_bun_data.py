from typing import List, Dict
from .lab_data import LabData
from phenopipe.vocab.terms.labs import BUN_TERMS


class AllBunData(LabData):
    date_col: str = "all_bun_entry_date"
    val_col: str = "all_bun_value"
    required_cols: List[str] = ["all_bun_value"]
    lab_terms: List[str] = BUN_TERMS
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
