from .sleep_levels_data import SleepLevelsData


class AllLightSleepData(SleepLevelsData):
    sql_aggregation: str = "all"
    sleep_levels: str = "light"
