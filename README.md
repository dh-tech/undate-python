# hackathon-2022

Repository for the DHTech 2022 Hackathon

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![unit tests](https://github.com/dh-tech/hackathon-2022/actions/workflows/unit_tests.yml/badge.svg)](https://github.com/dh-tech/hackathon-2022/actions/workflows/unit_tests.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## License

This software is licensed under the [Apache 2.0 License](LICENSE.md).

## Installation

To install the latest development version from GitHub:
```sh
pip install git+https://github.com/dh-tech/hackathon-2022.git@main#egg=undate
```

To install a specific release or branch, run the following (replace `[tag-name]` with the tag or branch you want to install):
```sh
pip install git+https://github.com/dh-tech/hackathon-2022.git@[tag-name]
```

## Instructions to setup for development

### Clone repo
```
$ git clone git@github.com:dh-tech/hackathon-2022.git
cd hackathon-2022
```

### Set up Python environment
Use a recent version of python 3.x; recommended to use a virtualenv, e.g.
```
python3 -m venv undate
source undate/bin/activate
```

### Install the package

Install an editable version of the local package along with python dependencies needed for testing and development.

```sh
pip install -e ".[dev]"
```

### Install pre-commit hooks
```sh
pre-commit install
```

### Run unit tests
```
pytest
```
