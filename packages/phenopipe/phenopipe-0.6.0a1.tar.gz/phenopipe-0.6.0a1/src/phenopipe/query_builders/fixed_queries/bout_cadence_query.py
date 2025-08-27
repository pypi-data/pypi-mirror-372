BOUT_CADENCE_QUERY = """
SELECT person_id,
				CAST(datetime AS DATE) as bout_cadence_date,
				AVG(steps) as bout_cadence_value
			FROM (SELECT steps_intraday.*,
						lag (datetime) over (partition by person_id, CAST(datetime AS DATE) order by datetime) as nextTimestamp_lag,
						lead (datetime) over (partition by person_id, CAST(datetime AS DATE) order by datetime) as nextTimestamp_lead
				from steps_intraday
				where steps >= 60 AND steps <= 250
				) t
			WHERE
			(DATE_DIFF(datetime,nextTimestamp_lag,minute) <= 1 OR
			DATE_DIFF(nextTimestamp_lead,datetime,minute) <= 1)
			GROUP BY
			CAST(datetime AS DATE),person_id
"""
