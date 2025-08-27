from typing import List, Dict
from .survey_data import SurveyData
from phenopipe.vocab.concepts.survey_questions import RENT_OWN_CODES


class RentOwnData(SurveyData):
    date_col: str = "rent_own_entry_date"
    val_col: str = "rent_own"
    survey_codes: List[str] = RENT_OWN_CODES
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
