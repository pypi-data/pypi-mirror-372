from phenopipe.tasks.get_data.fixed_query import FixedQuery
from phenopipe.query_builders.fixed_queries import DBP_QUERY


class GetDbp(FixedQuery):
    query: str = DBP_QUERY
