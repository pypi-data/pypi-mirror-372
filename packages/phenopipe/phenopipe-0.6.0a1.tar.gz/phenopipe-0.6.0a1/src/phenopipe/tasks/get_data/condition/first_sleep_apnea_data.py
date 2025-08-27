from typing import Optional, Dict, List
from .icd_condition_data import IcdConditionData
from phenopipe.vocab.icds.conditions import SLEEP_APNEA_ICDS


class FirstSleepApneaData(IcdConditionData):
    """
    Sleep apnea phenotype using icd condition occurance codes
    """

    #: if query is large according to google cloud api
    large_query: Optional[bool] = False

    aggregate: str = "first"

    date_col: str = "first_sleep_apnea_entry_date"

    icd_codes: Dict[str, List[str]] = SLEEP_APNEA_ICDS
