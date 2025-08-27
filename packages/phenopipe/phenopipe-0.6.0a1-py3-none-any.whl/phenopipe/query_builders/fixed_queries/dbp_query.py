DBP_QUERY = """
SELECT
        measurement.person_id,
        EXTRACT(DATE FROM measurement.measurement_datetime) as measurement_date,
        measurement.value_as_number
    FROM
        ( SELECT
            *
        FROM
            `measurement` measurement
        WHERE
            (
                measurement_concept_id IN  (
                    SELECT
                        DISTINCT c.concept_id
                    FROM
                        `cb_criteria` c
                    JOIN
                        (
                            select
                                cast(cr.id as string) as id
                            FROM
                                `cb_criteria` cr
                            WHERE
                                concept_id IN (
                                    4154790, 3012888, 3034703
                                )
                                AND full_text LIKE '%_rank1]%'
                        ) a
                            ON (
                                c.path LIKE CONCAT('%.',
                            a.id,
                            '.%')
                            OR c.path LIKE CONCAT('%.',
                            a.id)
                            OR c.path LIKE CONCAT(a.id,
                            '.%')
                            OR c.path = a.id)
                        WHERE
                            is_standard = 1
                            AND is_selectable = 1
                        )
                )
            ) measurement
"""
