from phenopipe.tasks.get_data.fixed_query import FixedQuery
from phenopipe.query_builders.fixed_queries import CADENCE_PATTERN_QUERY


class GetCadencePattern(FixedQuery):
    large_query: bool = True
    query: str = CADENCE_PATTERN_QUERY
