from typing import List
from .procedure_data import ProcedureData
from phenopipe.vocab.concepts.procedure import STENT_CODES


class FirstStentData(ProcedureData):
    aggregate: str = "first"
    date_col: str = "first_stent_entry_date"
    procedure_codes: List[str] = STENT_CODES
