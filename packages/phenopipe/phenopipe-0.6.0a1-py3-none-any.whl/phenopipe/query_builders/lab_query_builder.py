from typing import List, Optional


def lab_query(
    concept_codes: Optional[List[int]] = None, concept_names: Optional[List[str]] = None
):
    if concept_codes is None and concept_names is None:
        raise ValueError("Both concept codes and source values cannot be omitted.")

    if concept_codes is None:
        codes_str = "1<>1"
    else:
        codes_str = "c.concept_id IN (" + ", ".join(concept_codes) + ")"

    if concept_names is None:
        source_values_str = "1<>1"
    else:
        source_values_str = " OR ".join(
            [f"c.concept_name LIKE '{sv}'" for sv in concept_names]
        )

    query = f"""
            SELECT person_id, measurement_date, value_as_number, unit_source_value
            FROM `measurement` m
            INNER JOIN `concept` c ON (m.measurement_concept_id = c.concept_id)
            WHERE ({source_values_str}) OR {codes_str}
            """
    return query
