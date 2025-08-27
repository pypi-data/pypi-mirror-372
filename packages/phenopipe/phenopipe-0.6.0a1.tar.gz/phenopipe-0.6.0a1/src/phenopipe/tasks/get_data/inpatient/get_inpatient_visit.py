from phenopipe.tasks.get_data.fixed_query import FixedQuery
from phenopipe.query_builders.fixed_queries import INPATIENT_VISIT_QUERY


class GetInpatientVisit(FixedQuery):
    query: str = INPATIENT_VISIT_QUERY
