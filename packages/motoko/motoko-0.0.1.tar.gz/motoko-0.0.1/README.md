# Install the package in development mode with dependencies

```
pip install -e .
```


# Run the tests

```
pytest
```


# How to use Kusanagi

## Command line interface (CLI)

Kusanagi is provided with a few command lines.
In a Kusanagi directory equipped with a `motoko.yaml`file,
you can initialize the work flow with:

```
motoko create workflow_dir
cd workflow_dir
```

where `workflow_dir` is such a directory

You can then fetch for info of the current state:

```
motoko info
```

and to be more verbose

```
motoko info --verbose
```

You can finally kill every running daemon with:

```
motoko kill
```


## Python interface

TODO
