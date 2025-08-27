from typing import List, Dict
from .procedure_data import ProcedureData
from phenopipe.vocab.concepts.procedure import PCI_CODES


class AllPciData(ProcedureData):
    aggregate: str = "all"
    date_col: str = "all_pci_entry_date"
    procedure_codes: List[str] = PCI_CODES
    state: Dict[str, List[str]] = {"aou": "parsed", "std_omop": "untested"}
