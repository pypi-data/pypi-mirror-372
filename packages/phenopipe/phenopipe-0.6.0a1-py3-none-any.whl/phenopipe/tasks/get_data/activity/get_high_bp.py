from phenopipe.tasks.get_data.fixed_query import FixedQuery
from phenopipe.query_builders.fixed_queries import HIGH_BP_QUERY


class GetHighBp(FixedQuery):
    query: str = HIGH_BP_QUERY
