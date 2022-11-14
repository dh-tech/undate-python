# hackathon-2022

Repository for the DHTech 2022 Hackathon

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![unit tests](https://github.com/dh-tech/hackathon-2022/actions/workflows/unit_tests.yml/badge.svg)](https://github.com/dh-tech/hackathon-2022/actions/workflows/unit_tests.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-5-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->

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
Tests can be run with either `tox` or `pytest`.  

To run all the tests in a single test file, use pytest and specify the path to the test: `pytest tests/test_dateformat/test_base.py`

To test cases by name, use pytest: `pytest -k test_str`
### Create documentation
```
tox -e docs
```

## Contributors

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center"><a href="https://github.com/ColeDCrawford"><img src="https://avatars.githubusercontent.com/u/16374762?v=4?s=100" width="100px;" alt="Cole Crawford"/><br /><sub><b>Cole Crawford</b></sub></a><br /><a href="https://github.com/dh-tech/hackathon-2022/commits?author=ColeDCrawford" title="Code">💻</a> <a href="https://github.com/dh-tech/hackathon-2022/pulls?q=is%3Apr+reviewed-by%3AColeDCrawford" title="Reviewed Pull Requests">👀</a> <a href="https://github.com/dh-tech/hackathon-2022/commits?author=ColeDCrawford" title="Tests">⚠️</a></td>
      <td align="center"><a href="http://rlskoeser.github.io"><img src="https://avatars.githubusercontent.com/u/691231?v=4?s=100" width="100px;" alt="Rebecca Sutton Koeser"/><br /><sub><b>Rebecca Sutton Koeser</b></sub></a><br /><a href="https://github.com/dh-tech/hackathon-2022/commits?author=rlskoeser" title="Code">💻</a> <a href="https://github.com/dh-tech/hackathon-2022/pulls?q=is%3Apr+reviewed-by%3Arlskoeser" title="Reviewed Pull Requests">👀</a> <a href="https://github.com/dh-tech/hackathon-2022/commits?author=rlskoeser" title="Tests">⚠️</a></td>
      <td align="center"><a href="https://github.com/robcast"><img src="https://avatars.githubusercontent.com/u/1488847?v=4?s=100" width="100px;" alt="Robert Casties"/><br /><sub><b>Robert Casties</b></sub></a><br /><a href="#data-robcast" title="Data">🔣</a></td>
      <td align="center"><a href="https://github.com/jdamerow"><img src="https://avatars.githubusercontent.com/u/8881141?v=4?s=100" width="100px;" alt="Julia Damerow"/><br /><sub><b>Julia Damerow</b></sub></a><br /><a href="https://github.com/dh-tech/hackathon-2022/commits?author=jdamerow" title="Code">💻</a> <a href="https://github.com/dh-tech/hackathon-2022/pulls?q=is%3Apr+reviewed-by%3Ajdamerow" title="Reviewed Pull Requests">👀</a> <a href="https://github.com/dh-tech/hackathon-2022/commits?author=jdamerow" title="Tests">⚠️</a> <a href="#eventOrganizing-jdamerow" title="Event Organizing">📋</a></td>
      <td align="center"><a href="https://github.com/maltevogl"><img src="https://avatars.githubusercontent.com/u/20907912?v=4?s=100" width="100px;" alt="Malte Vogl"/><br /><sub><b>Malte Vogl</b></sub></a><br /><a href="https://github.com/dh-tech/hackathon-2022/commits?author=maltevogl" title="Code">💻</a> <a href="https://github.com/dh-tech/hackathon-2022/pulls?q=is%3Apr+reviewed-by%3Amaltevogl" title="Reviewed Pull Requests">👀</a> <a href="https://github.com/dh-tech/hackathon-2022/commits?author=maltevogl" title="Tests">⚠️</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->
