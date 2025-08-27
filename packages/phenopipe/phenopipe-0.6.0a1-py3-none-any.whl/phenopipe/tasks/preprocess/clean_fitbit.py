import datetime
import polars as pl
from phenopipe.tasks.task import Task, completion
from phenopipe.desc_funcs import summarize_n


class CleanFitbit(Task):
    wear_time_min: int = 10  #: minimum wear time for subsetting
    steps_min: int = 100  #: minimum steps for subsetting
    steps_max: int = 45_000  #: maximum steps for subsetting
    age_min: int = 18  #: minimum age for subsetting

    min_inputs_schemas: dict[str, dict] = {
        "fitbit": {"person_id": int, "steps": int},
        "demographics": {"person_id": int, "date_of_birth": datetime.date},
        "wear_time": {"person_id": int, "wear_time": int},
    }

    @completion
    def complete(self):
        """
        Clean fitbit daily activity summary dataframe with pre-determined thresholds
        Inputs:
        -------
         - fitbit: daily activity dataframe with columns (at least) person_id, date, steps
         - demographics: demographics dataframe with columns (at least) person_id, date_of_birth
         - wear_time: wear_time dataframe with columns (at least) person_id, date, wear_time

        Output:
        -------
         - cleaned daily activity summary dataframe
        """
        fitbit = self.inputs["fitbit"]
        demo = self.inputs["demographics"]
        wear_time = self.inputs["wear_time"]

        df = fitbit.join(
            demo.select("person_id", "date_of_birth"), on="person_id"
        ).join(
            wear_time.select("person_id", "date", "wear_time"), on=["person_id", "date"]
        )
        print("Initial Cohort")
        summarize_n(df)

        print(f"\nRemoving days where wear time < {self.wear_time_min} hrs.")
        df = df.filter(pl.col("wear_time") >= self.wear_time_min)
        summarize_n(df)

        print(f"\nRemoving days where step count < {self.steps_min}.")
        df = df.filter(pl.col("steps") >= self.steps_min)
        summarize_n(df)

        print(f"\nRemoving days where step counts > {self.steps_max}.")
        df = df.filter(pl.col("steps") <= self.steps_max)
        summarize_n(df)

        print(f"\nRemoving days where age < {self.age_min}.")
        df = df.filter(
            (pl.col("date") - pl.col("date_of_birth")).dt.total_days() / 365.25
            >= self.age_min
        )
        summarize_n(df)

        self.output = df
