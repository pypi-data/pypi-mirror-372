SLEEP_QUERY = """
SELECT
                  sleep_daily_summary.person_id
                , sleep_daily_summary.sleep_date as date
                , sleep_daily_summary.is_main_sleep
                , sleep_daily_summary.minute_in_bed
                , sleep_daily_summary.minute_asleep
                , sleep_daily_summary.minute_after_wakeup
                , sleep_daily_summary.minute_awake
                , sleep_daily_summary.minute_restless
                , sleep_daily_summary.minute_deep
                , sleep_daily_summary.minute_light
                , sleep_daily_summary.minute_rem
                , sleep_daily_summary.minute_wake
                FROM
                `sleep_daily_summary` sleep_daily_summary
"""
