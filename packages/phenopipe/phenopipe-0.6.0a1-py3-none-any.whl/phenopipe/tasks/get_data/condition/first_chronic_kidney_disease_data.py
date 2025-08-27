from typing import List, Dict
from .icd_condition_data import IcdConditionData
from phenopipe.vocab.icds.conditions import CHRONIC_KIDNEY_DISEASE_ICDS


class FirstChronicKidneyDiseaseData(IcdConditionData):
    aggregate: str = "first"
    date_col: str = "first_chronic_kidney_disease_entry_date"
    icd_codes: List[str] = CHRONIC_KIDNEY_DISEASE_ICDS
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
