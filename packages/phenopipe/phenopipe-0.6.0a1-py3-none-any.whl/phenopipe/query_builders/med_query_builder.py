from typing import List, Optional
from itertools import permutations


def med_query(med_names: Optional[List[str]] = None):
    def combine_med(med: Optional[List[str]]):
        return "|".join(map(".*".join, permutations(med)))

    meds = [combine_med(med) if isinstance(med, list) else med for med in med_names]

    med_names_str = " OR ".join([f"lower(c.concept_name) LIKE '%{mn}%'" for mn in meds])

    query = f"""
            SELECT DISTINCT d.person_id,d.drug_exposure_start_date
                FROM
                drug_exposure d
                INNER JOIN
                concept c
                ON (d.drug_concept_id = c.concept_id)
                WHERE ({med_names_str})
            """

    return query
