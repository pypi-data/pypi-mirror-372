from typing import List
from .inpatient_data import InpatientData
from phenopipe.vocab.icds.conditions import COPD_ICDS


class FirstCopdInpatientData(InpatientData):
    aggregate: str = "first"
    date_col: str = "first_copd_inpatient_entry_date"
    inp_codes: List[str] = COPD_ICDS
