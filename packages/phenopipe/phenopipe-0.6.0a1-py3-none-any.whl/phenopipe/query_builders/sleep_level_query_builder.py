from typing import List


def sleep_level_query(
    levels: List[str], sql_aggregation: str = "all", is_main_sleep: bool = True
):
    if isinstance(levels, str):
        levels = [levels]

    levels_str = " OR ".join([f"level = '{lev}'" for lev in levels])
    if is_main_sleep:
        levels_str = "(" + levels_str + ") AND is_main_sleep = 'true'"
    if sql_aggregation == "first":
        ordering = "asc"
    elif sql_aggregation == "last":
        ordering = "desc"
    elif sql_aggregation == "all":
        ordering = None
    else:
        raise ValueError("sql_aggregation parameter needs to be first, last or all")

    if sql_aggregation == "all":
        query = f"""
            SELECT person_id,
                    sleep_date AS sleep_date,
                    start_datetime AS sleep_datetime,
                    duration_in_min AS sleep_duration,
                    is_main_sleep AS is_main_sleep,
                    level AS sleep_level
                FROM
                    `sleep_level` sleep_level
                WHERE {levels_str}
        """
    else:
        query = f"""
            SELECT person_id,
                        sleep_date AS sleep_date,
                        start_datetime AS sleep_datetime,
                        duration_in_min AS sleep_duration,
                        is_main_sleep AS is_main_sleep,
                        level AS sleep_level
            FROM (SELECT person_id, sleep_date, start_datetime, duration_in_min, is_main_sleep, level,
                    row_number() over(partition by person_id, sleep_date order by start_datetime {ordering}) as rn
                    FROM sleep_level
                    WHERE {levels_str}) as t1
            WHERE rn = 1
        """

    return query
