from typing import List, Dict
from .medication_data import MedicationData
from phenopipe.vocab.terms.medications import CALCIUM_CHANNEL_BLOCKERS_TERMS


class FirstCalciumChannelBlockersData(MedicationData):
    date_col: str = "first_calcium_channel_blockers_entry_date"
    aggregate: str = "first"
    med_terms: List[str] = CALCIUM_CHANNEL_BLOCKERS_TERMS
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
