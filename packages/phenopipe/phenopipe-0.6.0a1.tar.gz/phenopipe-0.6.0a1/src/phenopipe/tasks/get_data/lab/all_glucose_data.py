from typing import List, Dict
from .lab_data import LabData
from phenopipe.vocab.terms.labs import GLUCOSE_TERMS


class AllGlucoseData(LabData):
    date_col: str = "all_glucose_entry_date"
    val_col: str = "all_glucose_value"
    required_cols: List[str] = ["all_glucose_value"]
    lab_terms: List[str] = GLUCOSE_TERMS
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
