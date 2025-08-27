from typing import List
from .medication_data import MedicationData
from phenopipe.vocab.terms.medications import STATINS_TERMS


class FirstStatinsData(MedicationData):
    aggregate: str = "first"
    date_col: str = "first_statins_entry_date"
    med_terms: List[str] = STATINS_TERMS
