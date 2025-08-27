from typing import List, Optional


def survey_query(survey_codes: Optional[List[str]]):
    survey_codes_str = ", ".join(survey_codes)

    query = f"""
            SELECT
            survey.person_id,
            survey.question AS survey_question,
            survey.answer AS survey_response,
            CAST(survey.survey_datetime AS DATE) AS survey_date
        FROM
            `ds_survey` survey
        WHERE
            (
                question_concept_id IN (
                          {survey_codes_str}
                )
            )"""
    return query
