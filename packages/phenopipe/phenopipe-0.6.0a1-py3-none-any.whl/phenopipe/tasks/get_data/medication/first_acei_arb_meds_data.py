from typing import List, Dict
from .medication_data import MedicationData
from phenopipe.vocab.terms.medications import ACE_INHIBITORS_TERMS, ARB_MEDS_TERMS


class FirstAceiArbMedsData(MedicationData):
    date_col: str = "first_acei_arb_meds_entry_date"
    aggregate: str = "first"
    med_terms: List[str] = ACE_INHIBITORS_TERMS + ARB_MEDS_TERMS
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
