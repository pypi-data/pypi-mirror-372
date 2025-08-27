from typing import List, Dict
from .procedure_data import ProcedureData
from phenopipe.vocab.concepts.procedure import THROMBOLYSIS_CODES


class AllThrombolysisData(ProcedureData):
    aggregate: str = "all"
    date_col: str = "all_thrombolysis_entry_date"
    procedure_codes: List[str] = THROMBOLYSIS_CODES
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
