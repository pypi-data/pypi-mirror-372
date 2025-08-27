from .sleep_levels_data import SleepLevelsData


class AllUnknownSleepData(SleepLevelsData):
    sql_aggregation: str = "all"
    sleep_levels: str = "unknown"
