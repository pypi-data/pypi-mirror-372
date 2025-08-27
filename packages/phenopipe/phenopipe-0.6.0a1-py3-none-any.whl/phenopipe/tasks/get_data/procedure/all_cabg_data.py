from typing import List, Dict
from .procedure_data import ProcedureData
from phenopipe.vocab.concepts.procedure import CABG_CODES


class AllCabgData(ProcedureData):
    aggregate: str = "all"
    date_col: str = "all_cabg_entry_date"
    procedure_codes: List[str] = CABG_CODES
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
