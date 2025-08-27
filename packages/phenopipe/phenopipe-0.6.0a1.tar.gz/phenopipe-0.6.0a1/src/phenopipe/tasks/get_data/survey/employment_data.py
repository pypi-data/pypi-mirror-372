from typing import List, Dict
from .survey_data import SurveyData
from phenopipe.vocab.concepts.survey_questions import EMPLOYMENT_CODES


class EmploymentData(SurveyData):
    date_col: str = "employment_entry_date"
    val_col: str = "employment"
    survey_codes: List[str] = EMPLOYMENT_CODES
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
