APPROX_RESTING_HR_QUERY = """
WITH step_tb AS 
    (
        SELECT person_id, 
            CAST(datetime AS DATE) AS date, 
            IF(COUNT(*)=10,1,0) AS valid_interval,
            FLOOR((EXTRACT(MINUTE FROM datetime) + 60 * EXTRACT(HOUR FROM datetime)) / 10) AS minute_interval
        FROM steps_intraday
        WHERE steps = 0
        GROUP BY person_id, date, minute_interval
        HAVING valid_interval = 1
    ),
    hr_tb AS 
    (
        SELECT person_id, 
            CAST(datetime AS DATE) AS date, 
            heart_rate_value,
            FLOOR((EXTRACT(MINUTE FROM datetime) + 60 * EXTRACT(HOUR FROM datetime)) / 10) AS minute_interval
        FROM heart_rate_minute_level
    )
    SELECT s.person_id, 
            s.date,
            APPROX_QUANTILES(heart_rate_value, 100)[OFFSET(10)] AS approx_resting_heart_rate
    FROM step_tb s
    INNER JOIN hr_tb h ON (s.person_id = h.person_id AND 
                            s.date = h.date           AND 
                            s.minute_interval = h.minute_interval)
    GROUP BY s.person_id, s.date
"""
