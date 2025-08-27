from typing import List
from .inpatient_data import InpatientData
from phenopipe.vocab.icds.conditions import MI_ICDS


class FirstMiInpatientData(InpatientData):
    aggregate: str = "first"
    date_col: str = "first_mi_inpatient_entry_date"
    inp_codes: List[str] = MI_ICDS
