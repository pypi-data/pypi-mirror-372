from typing import List, Dict
from .survey_data import SurveyData
from phenopipe.vocab.concepts.survey_questions import SMOKING_STOP_AGE_CODES


class SmokingStopAgeData(SurveyData):
    date_col: str = "smoking_stop_age_entry_date"
    val_col: str = "smoking_stop_age"
    survey_codes: List[str] = SMOKING_STOP_AGE_CODES
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
