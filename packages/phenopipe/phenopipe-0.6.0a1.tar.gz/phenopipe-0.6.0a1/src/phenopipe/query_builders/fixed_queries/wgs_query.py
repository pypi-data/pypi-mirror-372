WGS_QUERY = """
SELECT
            person.person_id
        FROM
            `person` person
        WHERE
            person.PERSON_ID IN (
                SELECT
                    distinct person_id
                FROM
                    `cb_search_person` cb_search_person
                WHERE cb_search_person.person_id IN (
                        SELECT
                            person_id
                        FROM
                            `cb_search_person` p
                        WHERE
                            has_whole_genome_variant = 1
"""
