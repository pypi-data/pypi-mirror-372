from typing import List, Dict
from .lab_data import LabData
from phenopipe.vocab.terms.labs import POTASSIUM_TERMS


class AllPotassiumData(LabData):
    date_col: str = "all_potassium_entry_date"
    val_col: str = "all_potassium_value"
    required_cols: List[str] = ["all_potassium_value"]
    lab_terms: List[str] = POTASSIUM_TERMS
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
