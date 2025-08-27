from phenopipe.tasks.get_data.fixed_query import FixedQuery
from phenopipe.query_builders.fixed_queries import SBP_QUERY


class GetSbp(FixedQuery):
    query: str = SBP_QUERY
