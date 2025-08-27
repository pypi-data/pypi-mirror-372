from typing import List, Dict
from .medication_data import MedicationData
from phenopipe.vocab.terms.medications import LOOP_DIURETICS_TERMS


class FirstLoopDiureticsData(MedicationData):
    date_col: str = "first_loop_diuretics_entry_date"
    aggregate: str = "first"
    med_terms: List[str] = LOOP_DIURETICS_TERMS
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
