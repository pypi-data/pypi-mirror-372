<img width="30%" style="display: block; margin-left: auto; margin-right: auto;" src=https://www.nicepng.com/png/detail/180-1803537_177kib-900x900-black-dynamite-black-dynamite.png>

# Quick start

## Documentation

The complete documentation of the project is on [readthedocs](https://blackdynamite.readthedocs.io/en/latest/)

## Installation

The easiest is through pip:

```bash
pip install blackdynamite
```

For a user scope installation (recommended):

```bash
pip install --user  blackdynamite
```

Or directly for the GitLab repository:

```bash
pip install  git+https://gitlab.com/ganciaux/blackdynamite.git
```


## Getting the sources

You can clone the GIT repository:

```bash
git clone https://gitlab.com/ganciaux/blackdynamite.git
```

## Installing completion

To benefit the autocompletion for **BlackDynamite** you need to
activate the global completion as described in the argcomplete website:
[Howto activate global completion](https://kislyuk.github.io/argcomplete/#activating-global-completion).

## Introduction and philosophy

**Blackdynamite** is merely a tool to help
managing parametric studies. In details it comprises:

1) Launching a program repeatedly with varying parameters, to explore the
  chosen parametric space.
  
2) Collect and sort results of **Small sizes** benefiting
  from the power of modern databases.
  
3) Analyze the results by making requests to the associated databases.


**Launching** is made simple by allowing any executable
to be launched. The set of directories will be generated and managed
by BlackDynamite to prevent errors. Requests of any kind will then
be made to the underlying database through friendly commands of BlackDynamite.

**Collecting** the results will be possible thanks to the Blackdynamite C/C++ and python
API which will let you send results directly to the database and thus automatically sort them. This is extremely useful. However heavy data such as Paraview files or any other kind of data should not be pushed to the database for obvious performance issues.

**Analysis** of the results can be made easy thanks to Blackdynamite which
can retrieve data information in the form of Numpy array to be used, analyzed or plotted
thanks to the powerful and vast Python libraries such as Matplotlib and Scipy.

The construction of a **BlackDynamite** parametric study follows these steps:

- Describing the parametric space
- Creating jobs (specific points in the parametric space)
- Creating runs (instances of the jobs)
- Launching runs
- Intrumenting the simulation to send results
- Analyzing the results

# Setting up a parametric study

The parametrization of a study is done in a YAML file, labelled
[bd.yaml](https://gitlab.com/ganciaux/blackdynamite/-/blob/master/example/bd.yaml).
It contains the information of the parametric space, spanned exploration and
configuration of your simulations. An example of a working study is provided in
the [example](https://gitlab.com/ganciaux/blackdynamite/-/tree/master/example) directory.

A study description starts with a provided name in the YAML format:

```yaml
---

study: bd_study
```

## Launching a unix/tcp daemon for the database

For convenience and parallel access to the database, a ZEO daemon is spawned
when using BlackDynamite.

You can see the status of the daemon with:

```
canYouDigIt server status
```

You can start/stop the server with the commands:

```
canYouDigIt server start
canYouDigIt server stop
```

By defaut the server is using a Unix socket for local usage.
If you need a tcp server to bind a port (for usage over a cluster for instance)
the server should be started with specific options:

```
canYouDigIt server start --host zeo://hostname:port
```


## Choose the parameters of the study

### Job description

The first thing to do is to list all the parameters characterizing 
a specific case. These parameters can
be of simple scalar types (e.g. string, integers, floats), however no
vectorial quantity can be considered as an input parameter.
It describes the `Job` pattern of the study.
This must be defined in a section in the the
[bd.yaml](https://gitlab.com/ganciaux/blackdynamite/-/blob/master/example/bd.yaml) file.
For instance a three parameter space can be declared as:

```yaml
job:
  param1: float
  param2: float
  param3: str

```

By default there is one more entry to every job: its unique `id`.


### Run description

Aside from the jobs, a run will represent a particular realisation (computation)
of a job. For instance, the run will contain information of the machine
it was run on, the executable version, or the number of processors employed.
For instance creating the run pattern can be done with:

```yaml
run:
  compiler: str
```

By default there are entries created for the user:

- id: the id of the run
- machine_name: the name of the machine where the run must be executed
- nproc: number of processors used to perform the computation (default: 1)
- run_path: the directory where the run will be created and launched
- job_id (integer): the ID of the running job
- state (str): the current state of the run (`CREATED`, `FINISHED`, `ERROR`)
- run_name (string): the name of the run (usually a name is given to a collection of runs, at creation)
- start_time (datetime): time when the run started
- last_step_time (datetime): last time a quantity was pushed to the database


## Create the database

Then you have to request for the creation of the database which can be done
with a simple command:
```bash
canYouDigIt init --truerun
```

As mentioned, all BlackDynamite
scripts inherit from the parsing system. So that when needing to launch
one of these codes, you can always claim for the valid keywords:
```bash
canYouDigIt init --help

usage: canYouDigIt [--study STUDY] [--host HOST] [--port PORT] [--user USER] [--password PASSWORD] [--bdconf BDCONF] [--truerun] [--constraints CONSTRAINTS]
                   [--binary_operator BINARY_OPERATOR] [--list_parameters] [--yes] [--logging] [--help]

createDB

General:
  --logging             Activate the file logging system (default: False)
  --help                Activate the file logging system (default: False)

BDParser:
  --study STUDY         Specify the study from the BlackDynamite database. This refers to the schemas in PostgreSQL language (default: None)
  --host HOST           Specify data base server address (default: None)
  --port PORT           Specify data base server port (default: None)
  --user USER           Specify user name to connect to data base server (default: tarantino)
  --password PASSWORD   Provides the password (default: None)
  --bdconf BDCONF       Path to a BlackDynamite file (*.bd) configuring current options (default: None)
  --truerun             Set this flag if you want to truly perform the action on base. If not set all action are mainly dryrun (default: False)
  --constraints CONSTRAINTS
                        This allows to constraint run/job selections by properties (default: None)
  --binary_operator BINARY_OPERATOR
                        Set the default binary operator to make requests to database (default: and)
  --list_parameters     Request to list the possible job/run parameters (default: False)
  --yes                 Answer all questions to yes (default: False)
```

An important point is that most of the actions are only applied
when the `truerun` flag is set. 

## Creating the jobs

The goal of the parametric study is to explore a subpart
of the parametric space. We need to create jobs that are
the points to explore. 

We need to describe the desired set of jobs, to be explored.
This is done in the YAML file describing the study, under the
section `job_space`. For instance it could be:

```yaml
job_space:
  param1: 10
  param2: [3.14, 1., 2.]
  param3: 'toto'
```

The actual insertion of jobs can be done with the command:

```python
canYouDigIt jobs create --truerun
```

You can control the created jobs with:

```python
canYouDigIt jobs info
```

In the case of our [example](https://gitlab.com/ganciaux/blackdynamite/-/tree/master/example), 3 jobs should be created
as a range of values for the second parameter was provided.


## Creating the runs

At this point the jobs are in the database. You need to create runs
that will precise the conditions of the realization of the jobs,
by giving the value of the run space.


This is specified in the YAML file under the section run_space. For instance
with:

```yaml
run_space:
  compiler: 'gcc'
```

The default parameters for runs will then be automatically
included in the parameters for the not provided ones (e.g. `state`).

A run now specify what action to perform to realize the job.
Therefore, one script must be provided as an entry point to each run execution.
This will be given in the YAML file as the `exec_file`. For instance from the
[example](https://gitlab.com/ganciaux/blackdynamite/-/tree/master/example)
a bash script is the entry point and provided as follows:

```yaml
exec_file: launch.sh
```

Usually, an end-user has a script(s) and configuration files
that he wishes to link to the run.
This can be done with:

```yaml
config_files:
  - config.txt
  - script.py
```

Finally, we have to create Run objects and attach them to jobs,
which is done with the command:

```bash
canYouDigIt runs create --truerun
```

After that, all created runs should be present in the database in the state
`CREATED`, ready to be launched. This can be controled with the command:

```bash
canYouDigIt runs info
```

## Instrumenting *Text* simulation files (e.g. a bash script)

`BlackDynamite` will replace specific text marks in the registered files
with the values from the job and run particular point. A precise syntax is
expected for `BlackDynamite` to recognize a replacement to be performed.

For instance:

```
echo __BLACKDYNAMITE__param1__
```

shall be replaced by the value of `param1` parameter at the run creation.

As an additional example, the script `launch.sh` taken 
from the [example](https://gitlab.com/ganciaux/blackdynamite/-/tree/master/example) has lines such as:

```
echo 'here is the job'
echo __BLACKDYNAMITE__id__
echo __BLACKDYNAMITE__param1__
echo __BLACKDYNAMITE__param2__
echo __BLACKDYNAMITE__param3__
```

## Instrumenting a *Python* simulation

In a python program, one can benefit from the possibilities of `Python` to
get a handle object on the current job and run.
This will also allow to push produced data to the database.
This is done by the simplified commands:

```python
# import BlackDynamite
import BlackDynamite as BD
# get the run from the current scope
myrun, myjob = BD.getRunFromScript()
```

In order to have time entries for runs, the functions `start` and `finish`
need to be called:

```python
myrun.start()
...
# your code
...
myrun.finish()
```

Finally, to push data directly to the database, one can use
`pushVectorQuantity` and/or `pushScalarQuantity`, attached to
meaurable `quantities`:

```python
# pushing vector types (numpy)
myrun.pushVectorQuantity(vector, step, "quantity_id")
# pushing scalar types 
myrun.pushScalarQuantity(scalar, step, "quantity_id")
```

## Executing the runs

Once the runs are created, they can be launched with a command like

```
canYouDigIt runs launch --truerun
```

During and after the run the status can be controlled, once again, with:

```bash
canYouDigIt runs info
```

For detailed information on a specific run:

```bash
canYouDigIt runs info --run_id RUN_ID_NUMBER
```

in order to be placed in the context of a specific run:

```bash
canYouDigIt runs info --run_id RUN_ID_NUMBER --enter
```

to execute a specific command

```bash
canYouDigIt runs info --exec COMMAND
```

and applied for a specific run:

```bash
canYouDigIt runs info --run_id RUN_ID_NUMBER --exec COMMAND
```

# Manipulating the database
## Selecting jobs and runs

All the previous commands may be applied to a subset of runs/jobs.
In order to select them one should place constraints, provided by
the option `--constraint`.
For instance, listing the runs constraining parameters
labeled `param1` and `param2` could be made with:

```bash
canYouDigIt runs info --constraint 'param1 > 1, param2 = 2'
```

In the exceptional case where parameters of jobs and runs would bear the same name
(you should avoid to do that), one can disambiguate the situation with:


```bash
canYouDigIt runs info --constraint 'jobs.id > 1, runs.id = 2'
```

## Cleaning Runs

Sometimes it can be necessary to re-launch a set of runs. Sometimes it
can be necessary to delete a run. In order to reset some runs,
making them ready to relaunch, one should use the following:

```bash
canYouDigIt runs clean --constraint 'jobs.id > 1, runs.id = 2' --truerun
```

To completely delete them:

```bash
canYouDigIt runs clean --constraint 'jobs.id > 1, runs.id = 2' --delete --truerun
```

## Altering runs

Rarely it can be necessary to manually change a set of runs. For instance changing the state of a set of runs can be done with:

```bash
canYouDigIt runs update --truerun state = toto
```

## Plotting results

For starting the exploration of the collected data, and thus producing graphs,
the `plot`command can be employed. While tunable, it cannot produce any type of graphs. However, for quick exploration of the data, one could do:

```bash
canYouDigIt runs plot --quantity ekin --legend "%r.id" --marker o
```

## Exporting the results (to zip file)

Under Construction

## Fecthing the results

A typical analysis of the results is made with a python script starting by building a database:

``` python
import BlackDynamite as BD
mybase = BD.Base()
```

In order to verify that the proper study was loaded, one can do

``` python
print(mybase.schema)
```

Making selections of runs and jobs can easily be done.
For instance, selecting all the runs in `FINISHED` state one can do:

``` python
params = {'constraints': ['state = FINISHED']}
runSelector = BD.RunSelector(mybase)
run_list = runSelector.selectRuns(params)
```

allowing to list the parameters

``` python
for r,j in run_list:
  print(r.entries.keys())
```

and to access them

``` python
for r,j in run_list:
  print(j.param1)
  print(r.compiler)
```

or to list the produced quantities

``` python
for r,j in run_list:
  print(r.listQuantities())
```

and to access them, returned as numpy arrays

``` python
for r,j in run_list:
  print(r.getScalarQuantity('ekin'))
```

To make graphs, one can:

``` python
import matplotlib.pyplot as plt

for r, j in run_list:
  steps, val = r.getScalarQuantity('ekin')
  times = steps * j.dt
  plt.plot(times, val, label=f"ekin param1={j.param1}")

plt.legend()
```



