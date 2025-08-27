from typing import List, Dict
from .survey_data import SurveyData
from phenopipe.vocab.concepts.survey_questions import ALCOHOL_CODES


class AlcoholData(SurveyData):
    date_col: str = "alcohol_entry_date"
    val_col: str = "alcohol"
    survey_codes: List[str] = ALCOHOL_CODES
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
