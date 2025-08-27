from phenopipe.tasks.get_data.fixed_query import FixedQuery
from phenopipe.query_builders.fixed_queries import WEAR_STUDY_QUERY


class GetWearStudy(FixedQuery):
    query: str = WEAR_STUDY_QUERY
