STATE_OF_RESIDENCY_QUERY = """
SELECT
        person_id,
        state_of_residence_source_value AS state_of_residence_value
    FROM
        person_ext
"""
