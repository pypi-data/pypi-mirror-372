from typing import List, Dict
from .procedure_data import ProcedureData
from phenopipe.vocab.concepts.procedure import CPAP_CODES


class FirstCpapData(ProcedureData):
    aggregate: str = "first"
    date_col: str = "first_cpap_entry_date"
    procedure_codes: List[str] = CPAP_CODES
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
