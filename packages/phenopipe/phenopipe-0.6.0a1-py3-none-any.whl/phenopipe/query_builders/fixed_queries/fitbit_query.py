FITBIT_QUERY = """
SELECT
                    activity_summary.person_id,
                    activity_summary.date,
                    activity_summary.steps,
                    activity_summary.fairly_active_minutes,
                    activity_summary.lightly_active_minutes,
                    activity_summary.sedentary_minutes,
                    activity_summary.very_active_minutes
                FROM
                    `activity_summary` activity_summary
"""
