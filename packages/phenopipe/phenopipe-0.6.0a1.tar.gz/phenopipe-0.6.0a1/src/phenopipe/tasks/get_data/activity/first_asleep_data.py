from .sleep_levels_data import SleepLevelsData


class FirstAsleepData(SleepLevelsData):
    sql_aggregation: str = "first"
    sleep_levels: str = ["deep", "light", "rem", "asleep"]
    is_main_sleep: bool = True
