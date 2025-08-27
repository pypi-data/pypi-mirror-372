from typing import List
from .icd_condition_data import IcdConditionData
from phenopipe.vocab.icds.conditions import PNES_ICDS


class FirstPnesData(IcdConditionData):
    """
    Psychogenic Nonepileptic Seizures (PNES) query
    """

    aggregate: str = "first"
    date_col: str = "first_pnes_entry_date"
    icd_codes: List[str] = PNES_ICDS
