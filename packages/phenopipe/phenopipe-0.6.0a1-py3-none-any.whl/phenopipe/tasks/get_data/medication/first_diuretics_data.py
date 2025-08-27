from typing import List, Dict
from .medication_data import MedicationData
from phenopipe.vocab.terms.medications import DIURETICS_TERMS


class FirstDiureticsData(MedicationData):
    date_col: str = "first_diuretics_entry_date"
    aggregate: str = "first"
    med_terms: List[str] = DIURETICS_TERMS
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
