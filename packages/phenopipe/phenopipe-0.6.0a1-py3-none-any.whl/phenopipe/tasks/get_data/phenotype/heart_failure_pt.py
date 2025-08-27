import polars as pl
from phenopipe.tasks.get_data.get_data import GetData
from phenopipe.tasks.task import completion
from phenopipe.vocab.icds.conditions import HEART_FAILURE_ICDS
from phenopipe.query_builders import icd_inpatient_query, icd_outpatient_query


class HeartFailurePt(GetData):
    cache_type: str = "std"

    date_col: str = "heart_failure_entry_date"

    @completion
    def complete(self):
        """
        Query heart failure phenotype defined as at least 1 inpatient or 2 outpatient ICD codes
        """
        inpatient_query = icd_inpatient_query(HEART_FAILURE_ICDS)
        outpatient_query = icd_outpatient_query(HEART_FAILURE_ICDS)

        inpatient_df = self.env_vars["query_conn"].get_query_rows(
            inpatient_query, return_df=True
        )
        outpatient_df = self.env_vars["query_conn"].get_query_rows(
            outpatient_query, return_df=True
        )

        def process_query_df(df, k):
            if isinstance(df.collect_schema().get("condition_start_date"), pl.String):
                df = df.output.with_columns(
                    pl.col("condition_start_date").str.to_date()
                )
            df = df.sort("condition_start_date").unique(
                ["person_id", "condition_start_date"]
            )
            df = (
                df.group_by("person_id")
                .agg(pl.col("condition_start_date").sort())
                .with_columns(
                    pl.col("condition_start_date").list.get(k, null_on_oob=True)
                )
            )
            return df

        in_out_count = process_query_df(inpatient_df, 0).join(
            process_query_df(outpatient_df, 1),
            on="person_id",
            how="full",
            coalesce=True,
            suffix="_out",
        )
        heart_failure_df = (
            in_out_count.with_columns(
                pl.min_horizontal(pl.exclude("person_id")).alias(
                    "heart_failure_entry_date"
                )
            )
            .select("person_id", "heart_failure_entry_date")
            .filter(pl.col("heart_failure_entry_date").is_not_null())
        )
        self.output = heart_failure_df

    def set_output_dtypes_and_names(self):
        self.set_date_column_dtype()
