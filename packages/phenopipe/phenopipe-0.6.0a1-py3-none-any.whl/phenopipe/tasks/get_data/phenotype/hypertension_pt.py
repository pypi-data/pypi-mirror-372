from phenopipe.tasks.get_data.get_data import GetData
from phenopipe.tasks.task import completion
from phenopipe.vocab.terms.medications import ANTI_HYPERTENSIVES_TERMS
from phenopipe.query_builders import med_query
from phenopipe.query_builders.fixed_queries import HIGH_BP_QUERY


class HypertensionPt(GetData):
    cache_type: str = "std"

    date_col: str = "hypertension_entry_date"

    @completion
    def complete(self):
        """
        Query hypertension phenotype defined as at least 1 medication or 1 hbp record
        """
        ht_med_query = med_query(ANTI_HYPERTENSIVES_TERMS)
        ht_med_df = self.env_vars["query_conn"].get_query_rows(
            ht_med_query, return_df=True
        )
        ht_med_df = ht_med_df.rename({"drug_exposure_start_date": "entry_date"})

        hbp_df = self.env_vars["query_conn"].get_query_rows(
            HIGH_BP_QUERY, return_df=True
        )
        hbp_df = hbp_df.rename({"measurement_date": "entry_date"})

        df = (
            hbp_df.vstack(ht_med_df)
            .group_by("person_id")
            .min()
            .rename({"entry_date": "hypertension_entry_date"})
        )
        self.output = df

    def set_output_dtypes_and_names(self):
        self.set_date_column_dtype()
