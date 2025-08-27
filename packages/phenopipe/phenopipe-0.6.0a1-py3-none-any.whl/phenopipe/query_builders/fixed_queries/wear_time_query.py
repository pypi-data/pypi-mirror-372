WEAR_TIME_QUERY = """
SELECT person_id, date, SUM(has_hour) AS wear_time
                    FROM (SELECT person_id, CAST(datetime AS DATE) AS date, IF(SUM(steps)>0, 1, 0) AS has_hour
                          FROM `steps_intraday`
                          GROUP BY CAST(datetime AS DATE), EXTRACT(HOUR FROM datetime), person_id) t
                    GROUP BY date, person_id 
"""
