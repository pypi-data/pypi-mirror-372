from typing import List, Dict
from .survey_data import SurveyData
from phenopipe.vocab.concepts.survey_questions import INCOME_CODES


class IncomeData(SurveyData):
    date_col: str = "income_entry_date"
    val_col: str = "income"
    survey_codes: List[str] = INCOME_CODES
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
