from typing import List, Dict
from .survey_data import SurveyData
from phenopipe.vocab.concepts.survey_questions import SEXUAL_ORIENTATION_CODES


class SexualOrientationData(SurveyData):
    date_col: str = "sexual_orientation_entry_date"
    val_col: str = "sexual_orientation"
    survey_codes: List[str] = SEXUAL_ORIENTATION_CODES
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
