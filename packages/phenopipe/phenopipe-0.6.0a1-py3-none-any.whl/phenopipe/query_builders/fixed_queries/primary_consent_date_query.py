PRIMARY_CONSENT_DATE_QUERY = """
SELECT DISTINCT
            person_id,
            MIN(observation_date) AS primary_consent_date
            FROM `concept`
            JOIN `concept_ancestor` on concept_id = ancestor_concept_id
            JOIN `observation` on descendant_concept_id = observation_source_concept_id
            WHERE concept_name = 'Consent PII' AND concept_class_id = 'Module'
            GROUP BY 1
"""
