from typing import List, Dict
from .lab_data import LabData
from phenopipe.vocab.terms.labs import FASTING_INSULIN_TERMS


class AllFastingInsulinData(LabData):
    date_col: str = "all_fasting_insulin_entry_date"
    val_col: str = "all_fasting_insulin_value"
    required_cols: List[str] = ["all_fasting_insulin_value"]
    lab_terms: List[str] = FASTING_INSULIN_TERMS
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
