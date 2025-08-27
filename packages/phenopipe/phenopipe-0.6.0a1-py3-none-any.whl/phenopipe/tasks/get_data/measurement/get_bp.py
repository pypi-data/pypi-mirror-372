from phenopipe.tasks.get_data.fixed_query import FixedQuery
from phenopipe.query_builders.fixed_queries import BP_QUERY


class GetBp(FixedQuery):
    query: str = BP_QUERY
