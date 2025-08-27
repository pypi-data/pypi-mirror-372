from typing import List
from .survey_data import SurveyData
from phenopipe.vocab.concepts.survey_questions import SMOKING_CURRENT_CODES


class SmokingCurrentData(SurveyData):
    date_col: str = "smoking_current_entry_date"

    survey_codes: List[str] = SMOKING_CURRENT_CODES

    val_col: str = "smoking"
