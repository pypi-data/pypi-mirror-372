from phenopipe.tasks.get_data.fixed_query import FixedQuery
from phenopipe.query_builders.fixed_queries import STATE_OF_RESIDENCY_QUERY


class GetStateOfResidency(FixedQuery):
    query: str = STATE_OF_RESIDENCY_QUERY
