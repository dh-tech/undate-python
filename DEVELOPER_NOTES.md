# Developer instructions

Ready to contribute to `undate`? Here are some instructions to get you started.

## Setup

### Use git to checkout a copy of the repository
```sh
git clone git@github.com:dh-tech/undate-python.git
cd undate-python
```

### Install and initialize git flow

This repository uses [git-flow](https://github.com/nvie/gitflow) branching conventions:
- **main** will always contain the most recent release
- **develop** branch is the latest version of work in progress

Pull requests for new features should be made against the **develop** branch.

We recommended installing git-flow.
1. On OSX, use brew or ports, e.g.: `brew install git-flow`; on Ubuntu/Debian, `apt-get install git-flow`
2. Initialize it in your local copy of this repository: run `git flow init` and accept all the defaults.
3. Use `git flow feature start feature-name` to create a new feature development branch.
4. Feature branches can be merged locally with git flow or by GitHub pull request.
4. Use git flow for releases with `git flow release start x.x.x` and `git flow release finish x.x.x`, where x.x.x is the version number for the new release.

If you cannot or prefer not to install git flow, you can do the equivalent manually.
1. Check out the develop branch: `git checkout develop`
3. Create new feature manually from the develop branch: `git checkout -b feature/xxx-name`

### Create a Python virtual environment

Use a recent version of python 3 (we recommend 3.12).  If you use [pyenv](https://github.com/pyenv/pyenv), run `pyenv install` to get the current recommended python version for development (specified in `.pythonversion`).

We highly recommend using a python virtualenv to isolate dependencies, e.g.
```
python3 -m venv .venv
source .venv/bin/activate
```

### Install local version of undate with development python dependencies

Install an editable version of the local package along with python dependencies needed for testing and development.

```sh
pip install -e ".[dev]"
```

### Install pre-commit hooks

We use [pre-commit](https://pre-commit.com/) for automated checks and consistent formatting.  If you're planning to contribute, please install these when you set up your local development.

```sh
pre-commit install
```

## Tests, documentation, and other checks

### Running unit tests

Tests can be run with `pytest`.

To run all the tests in a single test file, specify the path, e.g.: `pytest tests/test_dateformat/test_base.py`

To test cases by method name, use `-k`: `pytest -k test_str`

### Check python types

Python typing is currently enforced on pull requests as part of a GitHub Actions Continuous Integration check using `mypy` and via pre-commit hook.

To check types locally:
1. Install the necessary typing libraries (first run only):
```sh
mypy --install-types
```
2. Run `mypy src/` to check types.

### Documentation

Documentation can be built with sphinx. Make sure you have the dependencies installed:

```sh
pip install -e ".[docs]"
```

```sh
sphinx-build docs docs/_build
```

HTML documentation will be generated in `docs/_build/html`