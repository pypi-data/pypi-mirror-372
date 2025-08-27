from phenopipe.tasks.get_data.fixed_query import FixedQuery
from phenopipe.query_builders.fixed_queries import DEPRIVATION_INDEX_QUERY


class GetDeprivationIndex(FixedQuery):
    query: str = DEPRIVATION_INDEX_QUERY
