from phenopipe.tasks.get_data.fixed_query import FixedQuery
from phenopipe.query_builders.fixed_queries import WEIGHT_QUERY


class GetWeight(FixedQuery):
    query: str = WEIGHT_QUERY
