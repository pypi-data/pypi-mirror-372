from typing import List, Dict
from .survey_data import SurveyData
from phenopipe.vocab.concepts.survey_questions import GENDER_IDENTITY_CODES


class GenderIdentityData(SurveyData):
    date_col: str = "gender_identity_entry_date"
    val_col: str = "gender_identity"
    survey_codes: List[str] = GENDER_IDENTITY_CODES
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
