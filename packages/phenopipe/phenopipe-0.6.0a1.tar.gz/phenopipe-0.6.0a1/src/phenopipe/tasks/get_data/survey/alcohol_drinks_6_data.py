from typing import List, Dict
from .survey_data import SurveyData
from phenopipe.vocab.concepts.survey_questions import ALCOHOL_DRINKS_6_CODES


class AlcoholDrinks6Data(SurveyData):
    date_col: str = "alcohol_drinks_6_entry_date"
    val_col: str = "alcohol_drinks_6"
    survey_codes: List[str] = ALCOHOL_DRINKS_6_CODES
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
