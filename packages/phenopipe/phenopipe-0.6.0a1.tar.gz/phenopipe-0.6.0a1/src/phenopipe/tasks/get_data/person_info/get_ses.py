from phenopipe.tasks.get_data.fixed_query import FixedQuery
from phenopipe.query_builders.fixed_queries import SES_QUERY


class GetSes(FixedQuery):
    query: str = SES_QUERY
