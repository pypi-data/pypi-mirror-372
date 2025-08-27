INPATIENT_VISIT_QUERY = """
SELECT person_id,visit_start_date
            FROM
               visit_occurrence
            WHERE
                visit_concept_id IN (9201,9203)
"""
