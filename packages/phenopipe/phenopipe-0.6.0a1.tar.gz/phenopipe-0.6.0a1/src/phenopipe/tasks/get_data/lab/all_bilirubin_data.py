from typing import List, Dict
from .lab_data import LabData
from phenopipe.vocab.terms.labs import BILIRUBIN_TERMS


class AllBilirubinData(LabData):
    date_col: str = "all_bilirubin_entry_date"
    val_col: str = "all_bilirubin_value"
    required_cols: List[str] = ["all_bilirubin_value"]
    lab_terms: List[str] = BILIRUBIN_TERMS
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
