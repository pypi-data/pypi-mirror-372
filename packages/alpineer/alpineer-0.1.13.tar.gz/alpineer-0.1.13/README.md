# Alpineer

<div align="center">

| | |
| ---        |    ---  |
| CI / CD | [![CI](https://github.com/angelolab/alpineer/actions/workflows/ci.yml/badge.svg)](https://github.com/angelolab/alpineer/actions/workflows/ci.yml) [![Coverage Status](https://coveralls.io/repos/github/angelolab/alpineer/badge.svg?branch=main)](https://coveralls.io/github/angelolab/alpineer?branch=main) |
| Package | [![PyPI - Version](https://img.shields.io/pypi/v/alpineer.svg?logo=pypi&label=PyPI&logoColor=gold)](https://pypi.org/project/alpineer/) [![PyPI - Downloads](https://img.shields.io/pypi/dm/alpineer.svg?color=blue&label=Downloads&logo=pypi&logoColor=gold)](https://pypi.org/project/alpineer/) [![PyPI - Python Version](https://img.shields.io/pypi/pyversions/alpineer.svg?logo=python&label=Python&logoColor=gold)](https://pypi.org/project/alpineer/) |
|Meta | [![code style - Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) [![types - Mypy](https://img.shields.io/badge/types-Mypy-blue.svg)](https://github.com/python/mypy) [![PyPI - License](https://img.shields.io/pypi/l/alpineer?color=9400d3)](LICENSE) |
</div>

Toolbox for Multiplexed Imaging. Contains scripts and little tools which are used throughout [ark-analysis](https://github.com/angelolab/ark-analysis), [mibi-bin-tools](https://github.com/angelolab/mibi-bin-tools), and [toffy](https://github.com/angelolab/toffy)

- [alpineer](#alpineer)
  - [Requirements](#requirements)
  - [Setup](#setup)
  - [Development Notes](#development-notes)
  - [Questions?](#questions)

## Requirements

* [Python Poetry](https://python-poetry.org)
  * Recommeded to install it with either:
    * [**Official Installer:**](https://python-poetry.org/docs/master/#installing-with-the-official-installer)
        ```sh
        curl -sSL https://install.python-poetry.org | python3 -
        ```
    * [**pipx**](https://python-poetry.org/docs/master/#installing-with-pipx), (requires [`pipx`](https://pypa.github.io/pipx/))
      * If you are using `pipx`, run the following installation commands
        ```sh
        brew install pipx
        pipx ensurepath
        ```
* [pre-commit](https://pre-commit.com)
    ```sh
    brew isntall pre-commit
    ```

## Setup

1. Clone the repo: `git clone https://github.com/angelolab/alpineer.git`
2. `cd` into `alpineer`.
3. Install the pre-commit hooks with `pre-commit install`
4. Set up `python-poetry` for `alpineer`
   1. Run `poetry install` to install `alpineer` into your virtual environment. (Poetry utilizes [Python's Virtual Environments](https://docs.python.org/3/tutorial/venv.html))
   2. Run `poetry install --with test`: Installs all the [dependencies needed for tests](pyproject.toml) (labeled under `tool.poetry.group.test.dependencies`)
   3. Run `poetry install --with dev`: Installs all the [dependencies needed for development](pyproject.coml) (labeled under `tool.poetry.group.dev.dependencies`)
   4. You may combine these as well with `poetry install --with dev,test`. Installing the base dependencies and the two optional groups.
5. In order to test to see if Poetry is working properly, run `poetry show --tree`. This will output the dependency tree for the base dependencies (labeled under `tool.poetry.dependencies`).

    Sample Output:

   ```sh
   matplotlib 3.6.1 Python plotting package
   ├── contourpy >=1.0.1
   │   └── numpy >=1.16
   ├── cycler >=0.10
   ├── fonttools >=4.22.0
   ├── kiwisolver >=1.0.1
   ├── numpy >=1.19
   ├── packaging >=20.0
   │   └── pyparsing >=2.0.2,<3.0.5 || >3.0.5
   ├── pillow >=6.2.0
   ├── pyparsing >=2.2.1
   ├── python-dateutil >=2.7
   │   └── six >=1.5
   └── setuptools-scm >=7
       ├── packaging >=20.0
       │   └── pyparsing >=2.0.2,<3.0.5 || >3.0.5
       ├── setuptools *
       ├── tomli >=1.0.0
       └── typing-extensions *
   natsort 8.2.0 Simple yet flexible natural sorting in Python.
   numpy 1.23.4 NumPy is the fundamental package for array computing with Python.
   pillow 9.1.1 Python Imaging Library (Fork)
   pip 22.3 The PyPA recommended tool for installing Python packages.
   tifffile 2022.10.10 Read and write TIFF files
   └── numpy >=1.19.2
   ```


## Development Notes

1. I'd highly suggest refering to Poetry's extensive documentation on [installing packages](https://python-poetry.org/docs/master/cli/#add), [updating packages](https://python-poetry.org/docs/master/cli/#update) and more.
2. Tests can be ran with `poetry run pytest`. No additional arguments needed, they are all stored in the [`pyproject.toml`](pyproject.toml) file.
   1. As an aside, if you need to execute code in the poetry venv, use prefix your command with [`poetry run`](https://python-poetry.org/docs/master/cli/#run)

## Updating

* In order to update `alpineer`'s dependencies we can run:
  *  `poetry update`: for all dependencies
  *  `poetry update <package>`: where `<package>` can be something like `numpy`.
* To update Poetry itself, run `poetry self update`.
## Questions?

Feel free to open an issue on our [GitHub page](https://github.com/angelolab/alpineer/issues)
