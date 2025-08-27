from phenopipe.vocab.concepts.condition_type import OUTPATIENT_HEADERS
from phenopipe.vocab.concepts.visits import OUTPATIENT
from .icd_clause_builder import icd_clause


def icd_outpatient_query(icd_codes: dict[str, list]):
    icd_str = icd_clause(icd_codes=icd_codes)
    query = f"""
            SELECT co.person_id,co.condition_start_date,co.condition_source_value
            FROM
                `condition_occurrence` co
                LEFT JOIN
                `concept` c
                ON (co.condition_source_concept_id = c.concept_id)
                LEFT JOIN
                `visit_occurrence` v
                ON (co.visit_occurrence_id = v.visit_occurrence_id)
            WHERE
                ({icd_str}) AND
                (co.condition_type_concept_id IN ({",".join(OUTPATIENT_HEADERS)}) OR
                v.visit_concept_id IN ({",".join(OUTPATIENT)}))
            """
    return query
