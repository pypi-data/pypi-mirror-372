from .sleep_levels_data import SleepLevelsData


class AllAwakeSleepData(SleepLevelsData):
    sql_aggregation: str = "all"
    sleep_levels: str = "awake"
