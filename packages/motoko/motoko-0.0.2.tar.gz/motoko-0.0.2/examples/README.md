# Workflow description

the file `motko.yaml` contains the description of the workflow

``` yaml
task_managers:
  mult:

  add:

  norm:

orchestrator: orchestrator.main

```

which says that the task_managers are located in the subdirectories `mult`, `add` and `norm`.
These are valid `BlackDynamite` studies. Then it also says that the orchestrator is in the file `orchestrator`, to be launched with the main function.

# How to initialize and launch this workflow


- Init the workflow

``` bash
motoko create .
```

- You can list the available information (you will see jobs and runs are empty)

``` bash
motoko info
```

- Start the daemons


``` bash
motoko launcher
```

In verbose mode you should see the daemons running

``` bash
motoko info --verbose
```

-  Starting the workflow

The orchestrator is located in the file `orchestrator.py`. It can receive values for
starting a dynamically linked list of jobs. To know the expected parameters you can hit:

``` bash
motoko orchestrator start --help
```

which will provide a contextual help. In the case of the example it takes two numbers
with the `--inputs` option:

``` bash
motoko orchestrator start --inputs x 2.1 3.1
```

When finished you can control the execution

``` bash
motoko info
```
