from typing import List
from .procedure_data import ProcedureData
from phenopipe.vocab.concepts.procedure import TOTAL_HIP_ARTHROPLASTY_CODES


class FirstTotalHipArthoplastyData(ProcedureData):
    aggregate: str = "first"
    date_col: str = "first_total_hip_arthoplasty_entry_date"
    procedure_codes: List[str] = TOTAL_HIP_ARTHROPLASTY_CODES
