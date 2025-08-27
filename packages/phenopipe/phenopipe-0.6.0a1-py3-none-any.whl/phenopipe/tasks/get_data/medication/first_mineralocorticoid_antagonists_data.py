from typing import List, Dict
from .medication_data import MedicationData
from phenopipe.vocab.terms.medications import MINERALOCORTICOID_ANTAGONISTS_TERMS


class FirstMineralocorticoidAntagonistsData(MedicationData):
    date_col: str = "first_mineralocorticoid_antagonists_entry_date"
    aggregate: str = "first"
    med_terms: List[str] = MINERALOCORTICOID_ANTAGONISTS_TERMS
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
