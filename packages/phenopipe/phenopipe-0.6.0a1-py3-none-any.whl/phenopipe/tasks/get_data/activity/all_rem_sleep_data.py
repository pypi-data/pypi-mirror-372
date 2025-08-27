from .sleep_levels_data import SleepLevelsData


class AllRemSleepData(SleepLevelsData):
    sql_aggregation: str = "all"
    sleep_levels: str = "rem"
