from typing import List
from .inpatient_data import InpatientData
from phenopipe.vocab.icds.conditions import PNEUMONIA_ICDS


class FirstPneumoniaInpatientData(InpatientData):
    aggregate: str = "first"
    date_col: str = "first_pneumonia_inpatient_entry_date"
    inp_codes: List[str] = PNEUMONIA_ICDS
