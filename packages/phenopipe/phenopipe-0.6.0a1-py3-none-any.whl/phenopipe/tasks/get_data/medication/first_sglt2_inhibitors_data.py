from typing import List, Dict
from .medication_data import MedicationData
from phenopipe.vocab.terms.medications import SGLT2_INHIBITORS_TERMS


class FirstSglt2InhibitorsData(MedicationData):
    date_col: str = "first_sglt2_inhibitors_entry_date"
    aggregate: str = "first"
    med_terms: List[str] = SGLT2_INHIBITORS_TERMS
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
