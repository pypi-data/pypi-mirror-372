WEIGHT_QUERY = """
SELECT
            measurement.person_id,
            measurement.measurement_date as weight_entry_date,
            measurement.value_as_number as weight_value,
            m_unit.concept_name as weight_unit
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
                                        3025315, 3013762
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
                LEFT JOIN
                `concept` m_unit
                    ON measurement.unit_concept_id = m_unit.concept_id
"""
