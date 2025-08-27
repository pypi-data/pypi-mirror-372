from typing import List, Optional, Dict
from .icd_clause_builder import icd_clause


def hospitalization_query(icd_codes: Optional[Dict[str, List[str]]] = None):
    icd_str = icd_clause(icd_codes=icd_codes)
    query = f"""
            SELECT  co.person_id,
                    vo.visit_start_date AS hospitalization_entry_date,
                    co.condition_source_value AS hospitalization_icd_code
            FROM
                `condition_occurrence` co
                LEFT JOIN concept c ON (co.condition_source_concept_id = c.concept_id)
                LEFT JOIN `visit_occurrence` vo ON (co.visit_occurrence_id = vo.visit_occurrence_id)
            WHERE
                c.VOCABULARY_ID LIKE 'ICD%' AND
                (
                    (vo.visit_concept_id = 9201 OR vo.visit_concept_id = 9203) 
                    AND
                    (co.condition_type_concept_id = 38000200 OR co.condition_status_concept_id = 4230359)
                ) AND
                ({icd_str})
            """
    return query
