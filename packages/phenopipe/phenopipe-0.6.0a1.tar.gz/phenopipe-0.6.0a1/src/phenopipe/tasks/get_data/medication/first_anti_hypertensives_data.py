from typing import List, Dict
from .medication_data import MedicationData
from phenopipe.vocab.terms.medications import ANTI_HYPERTENSIVES_TERMS


class FirstAntiHypertensivesData(MedicationData):
    date_col: str = "first_anti_hypertensives_entry_date"
    aggregate: str = "first"
    med_terms: List[str] = ANTI_HYPERTENSIVES_TERMS
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
