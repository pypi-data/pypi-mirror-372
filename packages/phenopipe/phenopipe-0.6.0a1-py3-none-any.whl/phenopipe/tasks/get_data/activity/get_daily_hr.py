from phenopipe.tasks.get_data.fixed_query import FixedQuery
from phenopipe.query_builders.fixed_queries import DAILY_HR_QUERY


class GetDailyHr(FixedQuery):
    large_query: bool = True
    query: str = DAILY_HR_QUERY
