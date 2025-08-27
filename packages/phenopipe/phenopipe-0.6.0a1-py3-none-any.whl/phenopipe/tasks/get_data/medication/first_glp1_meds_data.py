from typing import List, Dict
from .medication_data import MedicationData
from phenopipe.vocab.terms.medications import GLP1_MEDS_TERMS


class FirstGlp1MedsData(MedicationData):
    date_col: str = "first_glp1_meds_entry_date"
    aggregate: str = "first"
    med_terms: List[str] = GLP1_MEDS_TERMS
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
