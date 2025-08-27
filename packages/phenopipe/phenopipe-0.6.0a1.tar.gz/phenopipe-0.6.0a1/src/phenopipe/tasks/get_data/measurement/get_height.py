from phenopipe.tasks.get_data.fixed_query import FixedQuery
from phenopipe.query_builders.fixed_queries import HEIGHT_QUERY


class GetHeight(FixedQuery):
    query: str = HEIGHT_QUERY
