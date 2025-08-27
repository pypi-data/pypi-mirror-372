from typing import List
from .procedure_data import ProcedureData
from phenopipe.vocab.concepts.procedure import TOTAL_KNEE_ARTHROPLASTY_CODES


class FirstTotalKneeArthoplastyData(ProcedureData):
    aggregate: str = "first"
    date_col: str = "first_total_knee_arthoplasty_entry_date"
    procedure_codes: List[str] = TOTAL_KNEE_ARTHROPLASTY_CODES
