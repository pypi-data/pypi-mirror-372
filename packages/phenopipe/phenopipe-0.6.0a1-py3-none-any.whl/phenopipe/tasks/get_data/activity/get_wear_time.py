from phenopipe.tasks.get_data.fixed_query import FixedQuery
from phenopipe.query_builders.fixed_queries import WEAR_TIME_QUERY


class GetWearTime(FixedQuery):
    query: str = WEAR_TIME_QUERY
