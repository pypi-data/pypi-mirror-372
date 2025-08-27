DEPRIVATION_INDEX_QUERY = """
SELECT
            observation.person_id,
            observation.observation_date AS deprivation_index_entry_date,
            zip_code.deprivation_index AS deprivation_index_value
        FROM
            `zip3_ses_map` zip_code
        JOIN
            `observation` observation
                ON CAST(SUBSTR(observation.value_as_string,
            0,
            STRPOS(observation.value_as_string,
            '*') - 1) AS INT64) = zip_code.zip3
        WHERE
            observation.PERSON_ID IN (
                SELECT
                    distinct person_id
                FROM
                    `cb_search_person` cb_search_person
                WHERE
                    cb_search_person.person_id IN (
                        SELECT
                            person_id
                        FROM
                            `cb_search_person` p
                        WHERE
                            has_fitbit = 1
                    )
                )
                AND observation_source_concept_id = 1585250
                AND observation.value_as_string NOT LIKE 'Res%'
"""
