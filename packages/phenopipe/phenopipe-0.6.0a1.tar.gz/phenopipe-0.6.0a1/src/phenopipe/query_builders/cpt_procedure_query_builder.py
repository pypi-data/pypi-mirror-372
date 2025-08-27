from typing import List, Optional


def cpt_procedure_query(cpt_codes: Optional[List[str]]):
    cpt_codes_str = " OR ".join([f"c.CONCEPT_CODE LIKE '{cpt}'" for cpt in cpt_codes])

    query = f"""
            SELECT DISTINCT p.person_id,c.CONCEPT_CODE AS cpt_code,p.PROCEDURE_DATE AS entry_date
            FROM
                concept c,
                procedure_occurrence p
                WHERE
                c.VOCABULARY_ID like 'CPT4' AND
                c.CONCEPT_ID = p.PROCEDURE_SOURCE_CONCEPT_ID AND
                ({cpt_codes_str})"""
    return query
