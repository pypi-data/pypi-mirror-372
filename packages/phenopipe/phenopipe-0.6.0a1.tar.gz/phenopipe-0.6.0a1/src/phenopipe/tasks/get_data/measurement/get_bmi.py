from phenopipe.tasks.get_data.fixed_query import FixedQuery
from phenopipe.query_builders.fixed_queries import BMI_QUERY


class GetBmi(FixedQuery):
    query: str = BMI_QUERY
