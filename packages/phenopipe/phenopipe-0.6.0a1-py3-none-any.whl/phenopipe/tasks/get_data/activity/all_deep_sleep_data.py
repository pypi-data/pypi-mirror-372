from .sleep_levels_data import SleepLevelsData


class AllDeepSleepData(SleepLevelsData):
    sql_aggregation: str = "all"
    sleep_levels: str = "deep"
