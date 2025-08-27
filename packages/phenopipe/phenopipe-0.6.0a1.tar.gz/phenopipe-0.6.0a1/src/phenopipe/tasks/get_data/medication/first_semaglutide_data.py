from typing import List, Dict
from .medication_data import MedicationData
from phenopipe.vocab.terms.medications import SEMAGLUTIDE_TERMS


class FirstSemaglutideData(MedicationData):
    date_col: str = "first_semaglutide_entry_date"
    aggregate: str = "first"
    med_terms: List[str] = SEMAGLUTIDE_TERMS
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
