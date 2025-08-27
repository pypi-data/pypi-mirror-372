import inflection
from pydantic import computed_field
from phenopipe.tasks.get_data.get_data import GetData
from phenopipe.tasks.task import completion


class GetMedicalEncounter(GetData):
    #: which medical encounter to return (first/last/all)
    select: str = "last"

    @computed_field
    @property
    def task_name(self) -> str:
        return inflection.underscore(f"{self.__class__.__name__}_{self.select}")

    @completion
    def complete(self):
        """
        Query medical encounters (first/last) and update self.output with resulting dataframe
        """
        """Runs medical encounters query with given local and self.time_select (first/last)"""
        if self.select not in ["first", "last", "all", "count"]:
            raise ValueError("Unknown select statement!")
        if self.select in ["first", "last"]:
            match self.select:
                case "last":
                    q_select = "MAX"
                case "first":
                    q_select = "MIN"
            query = f"""
                    WITH ehr AS (
                    SELECT person_id, {q_select}(m.measurement_date) AS date
                    FROM `measurement` AS m
                    LEFT JOIN `measurement_ext` AS mm on m.measurement_id = mm.measurement_id
                    WHERE LOWER(mm.src_id) LIKE 'ehr site%'
                    GROUP BY person_id

                    UNION DISTINCT

                    SELECT person_id, {q_select}(m.condition_start_date) AS date
                    FROM `condition_occurrence` AS m
                    LEFT JOIN `condition_occurrence_ext` AS mm on m.condition_occurrence_id = mm.condition_occurrence_id
                    WHERE LOWER(mm.src_id) LIKE 'ehr site%'
                    GROUP BY person_id

                    UNION DISTINCT

                    SELECT person_id, {q_select}(m.procedure_date) AS date
                    FROM `procedure_occurrence` AS m
                    LEFT JOIN `procedure_occurrence_ext` AS mm on m.procedure_occurrence_id = mm.procedure_occurrence_id
                    WHERE LOWER(mm.src_id) LIKE 'ehr site%'
                    GROUP BY person_id

                    UNION DISTINCT

                    SELECT person_id, {q_select}(m.visit_end_date) AS date
                    FROM `visit_occurrence` AS m
                    LEFT JOIN `visit_occurrence_ext` AS mm on m.visit_occurrence_id = mm.visit_occurrence_id
                    WHERE LOWER(mm.src_id) LIKE 'ehr site%'
                    GROUP BY person_id

                    UNION DISTINCT

                    SELECT person_id, {q_select}(m.drug_exposure_start_date) AS date
                    FROM `drug_exposure` AS m
                    GROUP BY person_id
                    )

                    SELECT person_id, {q_select}(date) as {self.select}_medical_encounter_entry_date
                    FROM ehr
                    GROUP BY person_id
                """
        else:
            query = """
            WITH ehr AS (
            SELECT DISTINCT person_id, m.measurement_date AS date
            FROM `measurement` AS m
            LEFT JOIN `measurement_ext` AS mm on m.measurement_id = mm.measurement_id
            WHERE LOWER(mm.src_id) LIKE 'ehr site%'

            UNION DISTINCT

            SELECT DISTINCT person_id, m.condition_start_date AS date
            FROM `condition_occurrence` AS m
            LEFT JOIN `condition_occurrence_ext` AS mm on m.condition_occurrence_id = mm.condition_occurrence_id
            WHERE LOWER(mm.src_id) LIKE 'ehr site%'
            
            UNION DISTINCT

            SELECT DISTINCT person_id, m.procedure_date AS date
            FROM `procedure_occurrence` AS m
            LEFT JOIN `procedure_occurrence_ext` AS mm on m.procedure_occurrence_id = mm.procedure_occurrence_id
            WHERE LOWER(mm.src_id) LIKE 'ehr site%'

            UNION DISTINCT

            SELECT DISTINCT person_id, m.visit_end_date AS date
            FROM `visit_occurrence` AS m
            LEFT JOIN `visit_occurrence_ext` AS mm on m.visit_occurrence_id = mm.visit_occurrence_id
            WHERE LOWER(mm.src_id) LIKE 'ehr site%'
            
            UNION DISTINCT

            SELECT DISTINCT person_id, m.drug_exposure_start_date AS date
            FROM `drug_exposure` AS m
            )
            SELECT person_id, date as medical_encounter_entry_date
            FROM ehr
            """
        df = self.env_vars["query_conn"].get_query_df(
            query, self.task_name, self.lazy, self.cache, self.cache_local
        )
        if self.select == "count":
            df = df.group_by("person_id").len()
        self.output = df

    def set_output_dtypes_and_names(self):
        self.set_date_column_dtype(f"{self.select}_medical_encounter_entry_date")
