WEAR_STUDY_QUERY = """
SELECT
               person_id,
               resultsconsent_wear AS wear_study_consent,
               wear_consent_start_date AS wear_study_consent_start_date,
               wear_consent_end_date AS wear_study_consent_end_date
            FROM
                wear_study
"""
