from typing import List, Dict
from .medication_data import MedicationData
from phenopipe.vocab.terms.medications import ASPIRIN_TERMS


class FirstAspirinData(MedicationData):
    date_col: str = "first_aspirin_entry_date"
    aggregate: str = "first"
    med_terms: List[str] = ASPIRIN_TERMS
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
