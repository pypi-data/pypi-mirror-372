from .sleep_levels_data import SleepLevelsData


class FirstLightSleepData(SleepLevelsData):
    sql_aggregation: str = "first"
    sleep_levels: str = "light"
    is_main_sleep: bool = True
