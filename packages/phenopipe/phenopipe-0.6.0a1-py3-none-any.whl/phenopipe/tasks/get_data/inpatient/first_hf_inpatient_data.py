from typing import List
from .inpatient_data import InpatientData
from phenopipe.vocab.icds.conditions import HEART_FAILURE_ICDS


class FirstHfInpatientData(InpatientData):
    aggregate: str = "first"
    date_col: str = "first_hf_inpatient_entry_date"
    inp_codes: List[str] = HEART_FAILURE_ICDS
