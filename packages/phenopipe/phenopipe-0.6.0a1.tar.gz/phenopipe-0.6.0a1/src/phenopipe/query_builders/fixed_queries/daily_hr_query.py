DAILY_HR_QUERY = """
SELECT person_id, 
                    CAST(datetime AS DATE) AS date,
                    AVG(heart_rate_value) AS mean_daily_heart_rate, 
                    STDDEV(heart_rate_value) AS sd_daily_heart_rate
            FROM heart_rate_minute_level 
            GROUP BY CAST(datetime AS DATE), person_id
"""
