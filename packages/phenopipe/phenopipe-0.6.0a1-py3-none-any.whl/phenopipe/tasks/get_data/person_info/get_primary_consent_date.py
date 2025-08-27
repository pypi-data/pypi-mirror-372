from phenopipe.tasks.get_data.fixed_query import FixedQuery
from phenopipe.query_builders.fixed_queries import PRIMARY_CONSENT_DATE_QUERY


class GetPrimaryConsentDate(FixedQuery):
    query: str = PRIMARY_CONSENT_DATE_QUERY
