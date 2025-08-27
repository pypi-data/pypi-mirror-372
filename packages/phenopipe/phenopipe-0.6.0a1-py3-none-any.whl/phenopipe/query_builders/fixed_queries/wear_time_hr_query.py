WEAR_TIME_HR_QUERY = """
SELECT person_id, CAST(datetime AS DATE) AS date, COUNT(*) AS wear_time_hr
                FROM heart_rate_minute_level
                WHERE heart_rate_value > 0
                GROUP BY person_id, date
"""
