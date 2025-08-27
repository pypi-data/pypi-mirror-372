from typing import List
from phenopipe.tasks.get_data.get_data import GetData
from phenopipe.tasks.task import completion
from phenopipe.query_builders import survey_query


class SurveyData(GetData):
    survey_codes: List[str]

    @completion
    def complete(self):
        """
        Generic query for survey data
        """
        survey_query_str = survey_query(self.survey_codes)
        self.output = self.env_vars["query_conn"].get_query_df(
            survey_query_str, self.task_name, self.lazy, self.cache, self.cache_local
        )

    def set_output_dtypes_and_names(self):
        self.output = self.output.rename(
            {
                "survey_date": self.date_col,
                "survey_question": f"{self.val_col}_survey_question",
                "survey_response": f"{self.val_col}_survey_response",
            }
        ).select(
            "person_id",
            f"{self.val_col}_survey_question",
            f"{self.val_col}_survey_response",
            self.date_col,
        )
        self.set_date_column_dtype()
