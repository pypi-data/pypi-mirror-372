<div align="center">
   <img src="https://gitlab.com/outflow-project/outflow/-/raw/develop/docs/sections/images/logo.svg" width="500" style="max-width: 500px;">
</div>

<div align="center">

<a href="https://pypi.org/project/outflow/">
  <img src="https://img.shields.io/pypi/pyversions/outflow.svg" alt="python">
</a>

<a href="https://pypi.org/project/outflow/">
  <img alt="PyPI" src="https://img.shields.io/pypi/v/outflow">
</a>

<a href="https://gitlab.com/outflow-project/outflow/-/pipelines/master/latest">
  <img alt="pipeline status" src="https://gitlab.com/outflow-project/outflow/badges/master/pipeline.svg" />
</a>

<a href="https://gitlab.com/outflow-project/outflow/-/pipelines/master/latest">
  <img alt="coverage report" src="https://gitlab.com/outflow-project/outflow/badges/master/coverage.svg" />
</a>

<a href=https://github.com/ambv/black>
    <img src="https://img.shields.io/badge/code%20style-black-000000.svg">
</a>

<a href='https://docs.outflow.dev'>
  <img src='https://readthedocs.org/projects/outflow/badge/?version=latest' alt='Documentation Status' />
</a>

<a href="https://pypi.python.org/pypi/outflow">
  <img src="https://img.shields.io/pypi/l/outflow.svg" alt="license" />
</a>

<a href="https://discord.outflow.dev/">
  <img src="https://img.shields.io/badge/discord-support-7389D8?logo=discord&style=flat&logoColor=fff" alt="chat-discord-support" />
</a>

</div>

Outflow is a framework that helps you build and run task workflows.

The api is as simple as possible while still giving the user full control over the definition and execution of the
workflows.

**Feature highlight :**

- Simple but powerful API
- Support for **parallelized and distributed execution**
- Centralized **command line interface** for your pipeline commands
- Integrated **database** access, sqlalchemy models and alembic migrations
- Executions and exceptions logging for **tracability**
- Strict type and input/output checking for a **robust** pipeline

Check out our [documentation][outflow readthedocs] for more information.

[outflow readthedocs]: https://docs.outflow.dev

# Installing

Install and update using [pip](https://pip.pypa.io/en/stable/):

```
pip install -U outflow
```

# Quick start

## One file starter

First, create a `pipeline.py` script:

```python
# -- pipeline.py

from outflow.core.commands import Command, RootCommand
from outflow.core.pipeline import Pipeline
from outflow.core.tasks import as_task

# with the as_task decorator, the function will be automatically converted into a Task subclass
# the signature of the function, including the return type, is used to determine task inputs and outputs
@as_task
def GetValues() -> {"word1": str, "word2": str}:
    return {"word1": "Hello", "word2": "world!"}

# default values can also be used as inputs
@as_task
def Concatenate(word1: str, word2: str) -> {"result": str}:
    result = f"{word1} {word2}"
    return result  # you can return the value directly if your task has only one output

# A task can have side-effects and returns nothing
@as_task
def PrintResult(result: str):
    print(result)

@RootCommand.subcommand()
class HelloWorld(Command):
    def setup_tasks(self):
        # instantiate the tasks
        get_values = GetValues()
        concatenate = Concatenate(word2="outflow!")  # you can override task inputs value at instantiation
        print_result = PrintResult()

        # build the workflow
        get_values >> concatenate >> print_result


# instantiate and run the pipeline
with Pipeline(
        root_directory=None,
        settings_module="outflow.core.pipeline.default_settings",
        force_dry_run=True,
) as pipeline:
    result = pipeline.run()

```

and run your first Outflow pipeline:

```
$ python pipeline.py hello_world
```

## A robust, configurable and well-organized pipeline

You had a brief overview of Outflow's features and you want to go further. Outflow offers command line tools to help you to start your pipeline project.

First, we will need to auto-generate the pipeline structure -- a collection of files including the pipeline settings, the database and the cluster configuration, etc.

```
$ python -m outflow management create pipeline my_pipeline
```

Then, we have to create a plugin -- a dedicated folder regrouping the commands, the tasks as well as the description of the database (the models)

```
$ python -m outflow management create plugin my_namespace.my_plugin --plugin_dir my_pipeline/plugins/my_plugin
```

In the my_pipeline/settings.py file, add your new plugin to the plugin list:

```python
PLUGINS = [
    'outflow.management',
    'my_namespace.my_plugin',
]
```

and run the following command:

```
$ python ./my_pipeline/manage.py my_plugin
```

You'll see the following output on the command line:

```
 * outflow.core.pipeline.pipeline - pipeline.py:325 - INFO - No cluster config found in configuration file, running in a local cluster
 * my_namespace.my_plugin.commands - commands.py:49 - INFO - Hello from my_plugin
```

Your pipeline is up and running. You can now start adding new tasks and commands.

# Contributing

For guidance on setting up a development environment and how to make a contribution to Outflow, see the [contributing guidelines](https://gitlab.lam.fr/CONCERTO/outflow/-/blob/master/CONTRIBUTING.md).
