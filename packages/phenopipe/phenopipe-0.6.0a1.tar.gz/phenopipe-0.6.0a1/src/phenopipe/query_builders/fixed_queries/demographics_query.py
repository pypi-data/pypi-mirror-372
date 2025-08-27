DEMOGRAPHICS_QUERY = """
SELECT
                        person.person_id,
                        person.birth_datetime as date_of_birth,
                        p_race_concept.concept_name as race,
                        p_ethnicity_concept.concept_name as ethnicity,
                        p_sex_at_birth_concept.concept_name as sex
                    FROM
                        `person` person
                    LEFT JOIN
                        `concept` p_race_concept
                            ON person.race_concept_id = p_race_concept.concept_id
                    LEFT JOIN
                        `concept` p_ethnicity_concept
                            ON person.ethnicity_concept_id = p_ethnicity_concept.concept_id
                    LEFT JOIN
                        `concept` p_sex_at_birth_concept
                            ON person.sex_at_birth_concept_id = p_sex_at_birth_concept.concept_id
"""
