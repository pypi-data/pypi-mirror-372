from typing import List, Dict
from .survey_data import SurveyData
from phenopipe.vocab.concepts.survey_questions import ALCOHOL_DRINKS_TYPICAL_CODES


class AlcoholDrinksTypicalData(SurveyData):
    date_col: str = "alcohol_drinks_typical_entry_date"
    val_col: str = "alcohol_drinks_typical"
    survey_codes: List[str] = ALCOHOL_DRINKS_TYPICAL_CODES
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
