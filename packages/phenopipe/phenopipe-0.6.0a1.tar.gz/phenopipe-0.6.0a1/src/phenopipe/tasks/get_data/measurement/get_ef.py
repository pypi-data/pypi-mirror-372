from phenopipe.tasks.get_data.fixed_query import FixedQuery
from phenopipe.query_builders.fixed_queries import EF_QUERY


class GetEf(FixedQuery):
    query: str = EF_QUERY
