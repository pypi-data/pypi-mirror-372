from typing import List
from .procedure_data import ProcedureData
from phenopipe.vocab.concepts.procedure import CA_BYPASS_GRAFT


class FirstCaBypassGraftData(ProcedureData):
    aggregate: str = "first"
    date_col: str = "first_ca_bypass_graft_entry_date"
    procedure_codes: List[str] = CA_BYPASS_GRAFT
