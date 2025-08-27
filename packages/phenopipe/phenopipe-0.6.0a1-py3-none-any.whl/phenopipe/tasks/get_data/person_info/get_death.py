from phenopipe.tasks.get_data.fixed_query import FixedQuery
from phenopipe.query_builders.fixed_queries import DEATH_QUERY


class GetDeath(FixedQuery):
    query: str = DEATH_QUERY
