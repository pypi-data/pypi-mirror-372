HIGH_BP_QUERY = """
WITH diatb AS (SELECT
        person_id, measurement_datetime, value_as_number AS dia
        FROM `measurement` m
    WHERE
        m.measurement_source_value IN ('8462-4','271650006','8453-3')),
    systb AS (SELECT
        person_id, measurement_datetime, value_as_number AS sys
        FROM `measurement` m
    WHERE
        m.measurement_source_value IN ('8480-6','271649006','8459-0'))
    SELECT d.person_id, MIN(CAST(d.measurement_datetime AS DATE)) AS measurement_date
    FROM
    diatb d
    INNER JOIN systb s
    ON (d.person_id = s.person_id)
    WHERE
    d.measurement_datetime = s.measurement_datetime
    AND sys >= 140
    AND dia >= 90
    GROUP BY d.person_id
"""
