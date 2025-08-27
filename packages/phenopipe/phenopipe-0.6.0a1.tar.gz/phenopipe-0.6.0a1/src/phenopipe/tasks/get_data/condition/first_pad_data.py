from typing import List
from .icd_condition_data import IcdConditionData
from phenopipe.vocab.icds.conditions import PAD_ICDS


class FirstPadData(IcdConditionData):
    """
    First peripheral artery disease data
    """

    aggregate: str = "first"
    date_col: str = "first_pad_entry_date"
    icd_codes: List[str] = PAD_ICDS
