import datetime
from phenopipe.tasks.preprocess import CleanSleep
from phenopipe.tasks.task import completion
from phenopipe.desc_funcs import summarize_n


class CleanSleepWithEhr(CleanSleep):
    min_inputs_schemas: dict[str, dict] = {
        "sleep": {
            "person_id": int,
            "date": datetime.date,
            "minute_asleep": int,
            "is_main_sleep": bool,
        },
        "demographics": {"person_id": int, "date_of_birth": datetime.date},
        "last_medical_encounter": {"person_id": int},
    }

    @completion
    def complete(self):
        """
        Clean daily sleep metrics summary dataframe with pre-determined thresholds and subset records without last medical encounter
        Inputs:
        -------
         - sleep: daily sleep metrics dataframe with columns (at least) person_id, date, minute_asleep, is_main_sleep
         - demographics: demographics dataframe with columns (at least) person_id, date_of_birth
         - medical_encounter_last: last medical encounters dataframe with columns (at least) person_id

        Output:
        -------
         - cleaned daily sleep activity dataframe subsetted by ehr records
        """
        if not self.validate_min_inputs_schemas():
            raise ValueError("invalid inputs to clean fitbit data")
        super().complete()

        print("\nRemoving records with no medical encounters")
        lme = self.inputs["last_medical_encounter"]
        self.output = self.output.join(lme.select("person_id"), on=["person_id"])
        summarize_n(self.output)
