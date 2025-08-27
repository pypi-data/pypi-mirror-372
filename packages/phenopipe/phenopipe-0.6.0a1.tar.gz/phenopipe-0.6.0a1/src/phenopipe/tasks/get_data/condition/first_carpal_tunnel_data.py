from typing import List, Dict
from .icd_condition_data import IcdConditionData
from phenopipe.vocab.icds.conditions import CARPAL_TUNNEL_ICDS


class FirstCarpalTunnelData(IcdConditionData):
    aggregate: str = "first"
    date_col: str = "first_carpal_tunnel_entry_date"
    icd_codes: List[str] = CARPAL_TUNNEL_ICDS
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
