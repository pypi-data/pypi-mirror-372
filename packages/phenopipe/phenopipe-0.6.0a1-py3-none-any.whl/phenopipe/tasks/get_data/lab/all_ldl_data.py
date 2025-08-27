from typing import List, Dict
from .lab_data import LabData
from phenopipe.vocab.terms.labs import LDL_TERMS


class AllLdlData(LabData):
    date_col: str = "all_ldl_entry_date"
    val_col: str = "all_ldl_value"
    required_cols: List[str] = ["all_ldl_value"]
    lab_terms: List[str] = LDL_TERMS
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
