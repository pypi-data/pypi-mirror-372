from .sleep_levels_data import SleepLevelsData


class AllAsleepSleepData(SleepLevelsData):
    sql_aggregation: str = "all"
    sleep_levels: str = "asleep"
