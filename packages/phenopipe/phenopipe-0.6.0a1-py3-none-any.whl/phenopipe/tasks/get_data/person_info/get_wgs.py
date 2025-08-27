from phenopipe.tasks.get_data.fixed_query import FixedQuery
from phenopipe.query_builders.fixed_queries import WGS_QUERY


class GetWgs(FixedQuery):
    query: str = WGS_QUERY
