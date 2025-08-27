from typing import List, Dict
from .lab_data import LabData
from phenopipe.vocab.terms.labs import HEMOGLOBIN_TERMS


class AllHemoglobinData(LabData):
    date_col: str = "all_hemoglobin_entry_date"
    val_col: str = "all_hemoglobin_value"
    required_cols: List[str] = ["all_hemoglobin_value"]
    lab_terms: List[str] = HEMOGLOBIN_TERMS
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
