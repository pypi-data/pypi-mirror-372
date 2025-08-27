from .sleep_levels_data import SleepLevelsData


class FirstDeepSleepData(SleepLevelsData):
    sql_aggregation: str = "first"
    sleep_levels: str = "deep"
    is_main_sleep: bool = True
