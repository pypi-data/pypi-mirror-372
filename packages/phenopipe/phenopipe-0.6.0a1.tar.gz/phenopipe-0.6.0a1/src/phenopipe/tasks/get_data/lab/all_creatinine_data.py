from typing import List, Dict
from .lab_data import LabData
from phenopipe.vocab.terms.labs import CREATININE_TERMS


class AllCreatinineData(LabData):
    date_col: str = "all_creatinine_entry_date"
    val_col: str = "all_creatinine_value"
    required_cols: List[str] = ["all_creatinine_value"]
    lab_terms: List[str] = CREATININE_TERMS
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
