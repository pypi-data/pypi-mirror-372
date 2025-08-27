from phenopipe.tasks.get_data.fixed_query import FixedQuery
from phenopipe.query_builders.fixed_queries import DEATH_CAUSE_QUERY


class GetDeathCause(FixedQuery):
    query: str = DEATH_CAUSE_QUERY
