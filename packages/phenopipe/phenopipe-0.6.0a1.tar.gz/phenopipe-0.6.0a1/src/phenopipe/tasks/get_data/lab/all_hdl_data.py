from typing import List, Dict
from .lab_data import LabData
from phenopipe.vocab.terms.labs import HDL_TERMS


class AllHdlData(LabData):
    date_col: str = "all_hdl_entry_date"
    val_col: str = "all_hdl_value"
    required_cols: List[str] = ["all_hdl_value"]
    lab_terms: List[str] = HDL_TERMS
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
