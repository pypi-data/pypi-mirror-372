from typing import List, Dict
from .survey_data import SurveyData
from phenopipe.vocab.concepts.survey_questions import HEALTH_INSURANCE_CODES


class HealthInsuranceData(SurveyData):
    date_col: str = "health_insurance_entry_date"
    val_col: str = "health_insurance"
    survey_codes: List[str] = HEALTH_INSURANCE_CODES
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
