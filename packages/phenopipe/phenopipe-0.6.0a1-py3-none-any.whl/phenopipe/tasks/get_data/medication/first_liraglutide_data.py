from typing import List, Dict
from .medication_data import MedicationData
from phenopipe.vocab.terms.medications import LIRAGLUTIDE_TERMS


class FirstLiraglutideData(MedicationData):
    date_col: str = "first_liraglutide_entry_date"
    aggregate: str = "first"
    med_terms: List[str] = LIRAGLUTIDE_TERMS
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
