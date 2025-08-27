from .sleep_levels_data import SleepLevelsData


class AllWakeSleepData(SleepLevelsData):
    sql_aggregation: str = "all"
    sleep_levels: str = "wake"
