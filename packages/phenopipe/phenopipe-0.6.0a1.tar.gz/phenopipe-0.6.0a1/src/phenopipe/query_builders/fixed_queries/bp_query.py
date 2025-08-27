BP_QUERY = """

WITH diatb AS (SELECT
            person_id, measurement_datetime, value_as_number AS bp_diastolic
            FROM measurement m
        WHERE
            m.measurement_source_value IN ('8462-4','8453-3', '271650006')),
        systb AS (SELECT
            person_id, measurement_datetime, value_as_number AS bp_systolic
            FROM measurement m
        WHERE
            m.measurement_source_value IN ('8480-6','8459-0', '271649006'))
        SELECT d.person_id,
               CAST(d.measurement_datetime AS DATE) AS measurement_date,
               bp_systolic,
               bp_diastolic
        FROM
        diatb d
        INNER JOIN systb s
        ON (d.person_id = s.person_id)
        WHERE
        d.measurement_datetime = s.measurement_datetime
"""
