from phenopipe.tasks.get_data.fixed_query import FixedQuery
from phenopipe.query_builders.fixed_queries import SDANN_QUERY


class GetSdann(FixedQuery):
    large_query: bool = True
    query: str = SDANN_QUERY
