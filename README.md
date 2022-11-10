# hackathon-2022

Repository for the DHTech 2022 Hackathon


## License

This software is licensed under the [Apache 2.0 License](LICENSE.md).

## Installation

To install the latest version from GitHub::

   pip install git+https://github.com/dh-tech/hackathon-2022.git@main#egg=undate


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

### Install editable version of the local package and test+development
dependencies

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