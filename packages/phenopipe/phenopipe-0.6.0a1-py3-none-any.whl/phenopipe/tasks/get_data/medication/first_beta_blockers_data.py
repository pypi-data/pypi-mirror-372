from typing import List, Dict
from .medication_data import MedicationData
from phenopipe.vocab.terms.medications import BETA_BLOCKERS_TERMS


class FirstBetaBlockersData(MedicationData):
    date_col: str = "first_beta_blockers_entry_date"
    aggregate: str = "first"
    med_terms: List[str] = BETA_BLOCKERS_TERMS
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
