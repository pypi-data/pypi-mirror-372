from typing import List, Dict
from .lab_data import LabData
from phenopipe.vocab.terms.labs import CALCIUM_TERMS


class AllCalciumData(LabData):
    date_col: str = "all_calcium_entry_date"
    val_col: str = "all_calcium_value"
    required_cols: List[str] = ["all_calcium_value"]
    lab_terms: List[str] = CALCIUM_TERMS
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
