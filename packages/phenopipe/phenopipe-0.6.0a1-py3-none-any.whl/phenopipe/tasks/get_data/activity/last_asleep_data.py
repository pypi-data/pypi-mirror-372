from .sleep_levels_data import SleepLevelsData


class LastAsleepData(SleepLevelsData):
    sql_aggregation: str = "last"
    sleep_levels: str = ["deep", "light", "rem", "asleep"]
    is_main_sleep: bool = True
