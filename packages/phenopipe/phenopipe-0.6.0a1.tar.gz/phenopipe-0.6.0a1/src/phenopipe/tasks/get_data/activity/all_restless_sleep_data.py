from .sleep_levels_data import SleepLevelsData


class AllRestlessSleepData(SleepLevelsData):
    sql_aggregation: str = "all"
    sleep_levels: str = "restless"
