from typing import List, Dict
from .survey_data import SurveyData
from phenopipe.vocab.concepts.survey_questions import EDUCATION_CODES


class EducationData(SurveyData):
    date_col: str = "education_entry_date"
    val_col: str = "education"
    survey_codes: List[str] = EDUCATION_CODES
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
