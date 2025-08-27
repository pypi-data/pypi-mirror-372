from phenopipe.tasks.get_data.fixed_query import FixedQuery
from phenopipe.query_builders.fixed_queries import BOUT_CADENCE_QUERY


class GetBoutCadence(FixedQuery):
    large_query: bool = True
    query: str = BOUT_CADENCE_QUERY
