import yaml
from importlib import import_module
from pathlib import Path
from typing import TypeVar, List, Any, Dict
import inflection
from pydantic import BaseModel, computed_field
from phenopipe.tasks import Task
import phenopipe

PolarsDataFrame = TypeVar("polars.dataframe.frame.DataFrame")
PolarsLazyFrame = TypeVar("polars.lazyframe.frame.LazyFrame")


def build_pipe_from_dict(plan):
    pipe = Pipe(env_vars=plan["env_vars"])
    pipe.env_vars["query_conn"] = getattr(
        phenopipe.query_connections, inflection.camelize(pipe.env_vars["query_conn"])
    )()

    input_mapping = {}
    modules = {k: import_module(v) for k, v in plan["modules"].items()}
    cache = plan["cache"]
    lazy = plan["lazy"]
    tasks = plan["tasks"]
    for task_id, task in tasks.items():
        if task["task_name"].split(".")[0] == "modules":
            task_address = task["task_name"].split(".")
            task_class = getattr(modules[task_address[1]], task_address[2])
        else:
            task_class = getattr(
                import_module(".".join(task["task_name"].split(".")[:-1])),
                task["task_name"].split(".")[-1],
            )
        if "inputs" in list(task.keys()):
            input_mapping[task_id] = task["inputs"]
        task_obj = task_class(
            task_id=task_id,
            env_vars=pipe.env_vars,
            **{k: v for k, v in task.items() if k != "inputs"},
        )
        if hasattr(task_obj, "lazy"):
            task_obj.lazy = lazy
        if hasattr(task_obj, "cache"):
            task_obj.lazy = cache
        pipe.tasks.update({task_id: task_obj})
    input_mapping = {
        k: {el: pipe.tasks[w] for el, w in v.items()} for k, v in input_mapping.items()
    }
    for inp, tsk in input_mapping.items():
        pipe.tasks[inp].input_tasks.update(tsk)
    return pipe


def build_pipe_from_yaml_str(plan_str):
    plan = yaml.safe_load(plan_str)
    return build_pipe_from_dict(plan)


def build_pipe_from_yaml(file_name):
    return build_pipe_from_yaml_str(Path(file_name).read_text())


class Pipe(BaseModel):
    env_vars: Dict[str, Any] = {}
    tasks: List[Task] = {}

    @computed_field
    @property
    def outputs(self) -> Dict[str, PolarsDataFrame | PolarsLazyFrame]:
        return {
            k: v
            for k, v in self.tasks.items()
            if "anchor" not in list(v.inputs.keys()) + list(v.input_tasks.keys())
        }

    def run(self):
        for task in self.tasks.values():
            if not task.completed:
                task.env_vars = self.env_vars
                task.complete()
        for out in self.outputs.values():
            out.merge_with_anchored_data()
