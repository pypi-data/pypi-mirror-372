from typing import List, Dict
from .lab_data import LabData
from phenopipe.vocab.terms.labs import NON_HDL_TERMS


class AllNonHdlData(LabData):
    date_col: str = "all_non_hdl_entry_date"
    val_col: str = "all_non_hdl_value"
    required_cols: List[str] = ["all_non_hdl_value"]
    lab_terms: List[str] = NON_HDL_TERMS
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
