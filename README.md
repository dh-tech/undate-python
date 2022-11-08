# hackathon-2022

Repository for the DHTech 2022 Hackathon


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

### Install dependencies
```
$ pip install -r requirements-dev.txt
```

### Install pre-commit hooks
```
$ pre-commit install
```

### Run unit tests
```
python -m pytest
```