from typing import List, Dict
from .medication_data import MedicationData
from phenopipe.vocab.terms.medications import ACE_INHIBITORS_TERMS


class FirstAceInhibitorsData(MedicationData):
    date_col: str = "first_ace_inhibitors_entry_date"
    aggregate: str = "first"
    med_terms: List[str] = ACE_INHIBITORS_TERMS
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
