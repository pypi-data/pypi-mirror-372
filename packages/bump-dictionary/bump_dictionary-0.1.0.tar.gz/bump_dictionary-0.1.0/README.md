# Bump Neurobagel data dictionaries

[![Main branch checks status](https://img.shields.io/github/check-runs/neurobagel/bump-dictionary/main?style=flat-square&logo=github)](https://github.com/neurobagel/bump-dictionary/actions?query=branch:main)
[![Tests status](https://img.shields.io/github/actions/workflow/status/neurobagel/bump-dictionary/test.yaml?branch=main&style=flat-square&logo=github&label=tests)](https://github.com/neurobagel/bump-dictionary/actions/workflows/test.yaml)
[![Codecov](https://img.shields.io/codecov/c/github/neurobagel/bump-dictionary?style=flat-square&logo=codecov&link=https%3A%2F%2Fcodecov.io%2Fgh%2Fneurobagel%2Fbump-dictionary)](https://app.codecov.io/gh/neurobagel/bump-dictionary)
[![Python versions static](https://img.shields.io/badge/python-3.10%20%7C%203.11-blue?style=flat-square&logo=python)](https://www.python.org)
[![License](https://img.shields.io/github/license/neurobagel/bump-dictionary?style=flat-square&color=purple&link=LICENSE)](LICENSE)
[![PyPI - Version](https://img.shields.io/pypi/v/bump-dictionary?style=flat-square&logo=pypi&link=https%3A%2F%2Fimg.shields.io%2Fpypi%2Fv%2Fbump-dictionary)](https://pypi.org/project/bump-dictionary/)

`bump-dictionary` is a tool to help migrate your existing Neurobagel data dictionaries to the latest data dictionary schema.

## Installation

`bump-dictionary` currently works with Python 3.10+, and can be installed from [PyPI](https://pypi.org/project/bagel/) using `pip`:

1. (Recommended) Create and activate a Python virtual environment (using a tool such as [venv](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#create-and-use-virtual-environments)).

2. Install the `bump-dictionary` package into your virtual environment:
    ```bash
    pip install bump-dictionary
    ```

## Usage

To upgrade a Neurobagel data dictionary in your current directory named `my_old_dictionary.json`, run in your terminal:

```bash
bump-dictionary my_legacy_dictionary.json
```

By default, the updated data dictionary file will be saved to `./updated_dictionary.json`.

For full CLI help, run:
```
bump-dictionary -h
```

## Development environment

### Setting up a local development environment
1. Clone the repository

    ```bash
    git clone https://github.com/neurobagel/bump-dictionary.git
    cd bump-dictionary
    ```

2. Install the CLI and all development dependencies in editable mode:

    ```bash
    pip install -e ".[dev]"
    ```

Confirm that everything works well by running the tests: 
`pytest .`

### Setting up code formatting and linting (recommended)

[pre-commit](https://pre-commit.com/) is configured in the development environment for this repository, and can be set up to automatically run a number of code linters and formatters on any commit you make according to the consistent code style set for this project.

Run the following from the repository root to install the configured pre-commit "hooks" for your local clone of the repo:
```bash
pre-commit install
```

pre-commit will now run automatically whenever you run `git commit`.

### Updating dependencies
If new runtime or development dependencies are needed, add them to `pyproject.toml` using minimal version constraints.
