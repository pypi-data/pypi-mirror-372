from typing import List, Dict
from .survey_data import SurveyData
from phenopipe.vocab.concepts.survey_questions import SMOKING_CODES


class SmokingData(SurveyData):
    date_col: str = "smoking_entry_date"
    val_col: str = "smoking"
    survey_codes: List[str] = SMOKING_CODES
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
