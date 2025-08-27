from .sleep_levels_data import SleepLevelsData


class FirstWakeSleepData(SleepLevelsData):
    sql_aggregation: str = "first"
    sleep_levels: str = "wake"
    is_main_sleep: bool = True
