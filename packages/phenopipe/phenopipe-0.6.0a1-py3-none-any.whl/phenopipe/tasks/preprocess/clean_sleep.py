import datetime
import polars as pl
from phenopipe.tasks.task import Task, completion
from phenopipe.desc_funcs import summarize_n


class CleanSleep(Task):
    is_main_sleep: bool = True  #: either to subset non-main-sleep
    minutes_min: int = 0  #: minimum asleep minutes for subsetting
    minutes_max: int = 1_440  #: maximum asleep minutes for subsetting
    age_min: int = 18  #: minimum age for subsetting

    min_inputs_schemas: dict[str, dict] = {
        "sleep": {
            "person_id": int,
            "date": datetime.date,
            "minute_asleep": int,
            "is_main_sleep": bool,
        },
        "demographics": {"person_id": int, "date_of_birth": datetime.date},
    }

    @completion
    def complete(self):
        """
        Clean daily sleep metrics summary dataframe with pre-determined thresholds
        Inputs:
        -------
         - sleep: daily sleep metrics dataframe with columns (at least) person_id, date, minute_asleep, is_main_sleep
         - demographics: demographics dataframe with columns (at least) person_id, date_of_birth

        Output:
        -------
         - cleaned daily sleep activity dataframe
        """
        sleep = self.inputs["sleep"]
        demo = self.inputs["demographics"]

        df = sleep.join(demo.select("person_id", "date_of_birth"), on="person_id")

        print("Initial Cohort")
        summarize_n(df)

        print(f"\nRemoving days where minutes asleep < {self.minutes_min}.")
        df = df.filter(pl.col("minute_asleep") >= self.minutes_min)
        summarize_n(df)

        print(f"\nRemoving days where minutes asleep > {self.minutes_max}.")
        df = df.filter(pl.col("minute_asleep") <= self.minutes_max)
        summarize_n(df)

        print(f"\nRemoving days where age < {self.age_min}.")
        df = df.filter(
            (pl.col("date") - pl.col("date_of_birth")).dt.total_days() / 365.25
            >= self.age_min
        )
        summarize_n(df)

        if self.is_main_sleep:
            print("\nNon main sleep records are being removed.")
            df = df.filter(pl.col("is_main_sleep"))
        else:
            print("\nNon main sleep records are NOT filtered.")

        print("\nRemoving subjects > 30% days < 4 hours sleep")
        df = (
            df.join(
                df.select("person_id", "minute_asleep")
                .with_columns(pl.col("minute_asleep") < 4 * 60)
                .group_by("person_id")
                .mean(),
                on="person_id",
            )
            .filter(pl.col("minute_asleep_right") <= 0.3)
            .drop("minute_asleep_right")
        )
        self.output = df
