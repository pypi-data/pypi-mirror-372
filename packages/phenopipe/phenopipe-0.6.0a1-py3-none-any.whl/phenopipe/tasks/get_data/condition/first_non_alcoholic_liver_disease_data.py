from typing import List, Dict
from .icd_condition_data import IcdConditionData
from phenopipe.vocab.icds.conditions import NON_ALCOHOLIC_LIVER_DISEASE_ICDS


class FirstNonAlcoholicLiverDiseaseData(IcdConditionData):
    aggregate: str = "first"
    date_col: str = "first_non_alcoholic_liver_disease_entry_date"
    icd_codes: List[str] = NON_ALCOHOLIC_LIVER_DISEASE_ICDS
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
