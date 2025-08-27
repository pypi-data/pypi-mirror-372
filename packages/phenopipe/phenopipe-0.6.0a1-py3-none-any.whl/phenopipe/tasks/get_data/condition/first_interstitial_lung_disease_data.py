from typing import List, Dict
from .icd_condition_data import IcdConditionData
from phenopipe.vocab.icds.conditions import INTERSTITIAL_LUNG_DISEASE_ICDS


class FirstInterstitialLungDiseaseData(IcdConditionData):
    aggregate: str = "first"
    date_col: str = "first_interstitial_lung_disease_entry_date"
    icd_codes: List[str] = INTERSTITIAL_LUNG_DISEASE_ICDS
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
