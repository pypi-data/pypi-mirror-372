from typing import List, Dict
from .survey_data import SurveyData
from phenopipe.vocab.concepts.survey_questions import STABLE_HOUSE_CONCERN_CODES


class StableHouseConcernData(SurveyData):
    date_col: str = "stable_house_concern_entry_date"
    val_col: str = "stable_house_concern"
    survey_codes: List[str] = STABLE_HOUSE_CONCERN_CODES
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
