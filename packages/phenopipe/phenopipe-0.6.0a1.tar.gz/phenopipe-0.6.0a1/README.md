Phenopipe
---------------------------------------------

**Python Functions for Phenotyping and Analysis**

Phenopipe is a Python library to automate phenotyping and downstream analysis. Its main development target is All of Us research platform.
Phenopipe is heavily inspired by and borrowed query definitions from https://github.com/annisjs/aou.phenotyper2 and https://github.com/annisjs/aou.reader 

## Tasks
The basic building block in phenopipe library is a task which is a class from tasks module. A task represents a single step in phenotyping and 
analysis. Its inputs are polars dataframes and it has a single polars dataframe output. Therefore tasks' outputs can be passed to
other tasks. This can be automated using input_tasks attribute in task class. Each task in input_tasks will be completed 
prior to task completion and those outputs will be added to inputs. Each task need to have a complete method which contains the logic of the 
data retrieval and/or analysis step and completion decorator automates common operations prior and after task is completed.

## Data Queries
A common task type is getting the data from the database. These tasks are collected under get_data module in tasks module.
These tasks contains additional attributes such as caching and lazy dataframe evaulation. Data queries are planned by 
tasks but it is run inside query connection objects which are provided in query_connections module. The goal is to allow running the same 
data tasks on different platform by simply changing the query connection in enviroment variables. This is partially achieved for other platforms designed
around OMOP Data Model like AOU, however AOU specific data structures does not fully allow this. To track if a task is compatible (or tested) with a platform
state attribute is used. This attribute holds a key value pair where keys are shared with query platform attribute of query connections and values indicate if 
task is compatible. Value can be one of the followings:

incompatible: Indicates the task is known to be incompatible with the platform.
parsed: Indicates the task is parsed from another library and it is not yet tested.
untested: Indicates the task in not tested on this platform.
unverified: Indicates the resulting data is not yet verified.
tested: Indicates the task is tested on this platform
verified: Indicates the task is verified on this platform which means the resulting data is used in an analysis and didn't show any inconsistencies.


## Environment Variables
env_vars attribute in task object holds variables that is shared between different tasks. It is also used to share common variables between tasks in a analysis.
An example variable is query connection stored in env_vars to delegate communication with database.

## Plan
A Pipe object holds a phenotyping and analysis plan as a dictionary of tasks and a env_vars attribute. Pipe object has a run method which will complete each task and merge each result on its anchor. Only tasks outputs without any anchor is saved in outputs dictionary.

## Inputs
A task can accept other tasks or their outputs as inputs. Each task may have a minimal input schema which describes the minimal column names and data types in order to task to run succesfully. Similarly every task has a minimal output schema which describes the minimal column names and data types in the output dataframe so any task can determine if it accepts the task as input. All input schemas and output schema are validated during task completion.

## Anchor Input
Anchor keyword in inputs dictionary is reserved for a data frame defining a selection criteria of the output. This can be described using anchor_date, anchor_range, anchor_pid attributes in the task object. Anchor range list of two literal which can be column names in anchor input dataframe or integers determining the time window for selection around anchor_date_col column in anchor dataframe. Anchor pid is the name of the column of person ids in the anchor
dataframe to be used during subsetting.

## Data Aggregate
Any task can indicate an aggregate function that will be run after or alongside the anchoring. This can be first, last, closest:nearest, closest:forward, closest:backward. For closest aggregate an anchor needs to be given. Ties are broken randomly but consistently.  

## Templating
Phenopipe provides a templating structure to define a Pipe object using yaml files (or strings or dictionaries in the same format). The function build_pipe_from_yaml will accept the file name for a yaml. The pipe object obtained using example below will collect initial hypertension diagnosis where there is a heart failure hospitalization in one year window before or after and return with the first heart failure hospitalization date in that window. Each task is given as a absolute import import such as phenopipe.tasks.get_data.hospitalization.FirstHfHospitalizationData or commonly used modules can be described using modules keyword and relative import can be given such as modules.phenotype.HypertensionPt for convenience.
Query connection will be translated as the camelcase class of the underscored name given in the template. All parameters under the task id will be passed into task init method. The inputs of a task can be other tasks in the plan given by using the identifier.


```
target: examples
cache: false
lazy: false
env_vars:
  query_conn: big_query_connection
modules:
  phenotype: phenopipe.tasks.get_data.phenotype
tasks:
  hypertension:
    task_name: modules.phenotype.HypertensionPt
    cache_type: std
  first_hf_hospitalization:
    task_name: phenopipe.tasks.get_data.hospitalization.FirstHfHospitalizationData
    cache_type: std
    inputs:
      anchor: hypertension
    anchor_range: [-365, 365]
```