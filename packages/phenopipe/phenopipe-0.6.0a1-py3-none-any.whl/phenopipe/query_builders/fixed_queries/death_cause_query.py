DEATH_CAUSE_QUERY = """
SELECT
            DISTINCT d.person_id
            , d.death_cause_date
            , (SELECT concept_name FROM `concept` WHERE concept_id = cause_concept_id) as death_cause_value
        
        FROM `death` d
"""
