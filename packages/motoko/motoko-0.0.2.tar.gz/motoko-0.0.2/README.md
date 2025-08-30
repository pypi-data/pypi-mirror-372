<img width="20%" style="display: block; margin-left: auto; margin-right: auto;" src="https://gitlab.com/blackdynamite/motoko/-/raw/main/icon.png?ref_type=heads">

# How to use Motoko

## Command line interface (CLI)

Motoko 草薙素子 is provided with a few command lines.
In a Motoko directory equipped with a `motoko.yaml`file,
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


# Developments

## Install the package in development mode with dependencies

```
pip install -e .
```


## Run the tests

```
pytest
```

## Python interface

TODO
