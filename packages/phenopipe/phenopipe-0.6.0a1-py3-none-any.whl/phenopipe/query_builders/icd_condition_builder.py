from .icd_clause_builder import icd_clause


def icd_condition_query(icd_codes: dict[str, list]):
    icd_str = icd_clause(icd_codes=icd_codes)
    query = f"""
            SELECT DISTINCT co.person_id, co.condition_start_date,co.condition_source_value
            FROM
                condition_occurrence co
                INNER JOIN
                concept c
                ON (co.condition_source_concept_id = c.concept_id)
            WHERE
                ({icd_str})
            """
    return query
