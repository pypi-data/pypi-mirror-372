from typing import List, Dict
from .lab_data import LabData
from phenopipe.vocab.terms.labs import CARBON_DIOXIDE_TERMS


class AllCarbonDioxideData(LabData):
    date_col: str = "all_carbon_dioxide_entry_date"
    val_col: str = "all_carbon_dioxide_value"
    required_cols: List[str] = ["all_carbon_dioxide_value"]
    lab_terms: List[str] = CARBON_DIOXIDE_TERMS
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
