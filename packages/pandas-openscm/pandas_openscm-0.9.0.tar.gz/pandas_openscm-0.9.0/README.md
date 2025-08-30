<!--- --8<-- [start:description] -->
# Pandas-OpenSCM

Pandas accessors for OpenSCM-related functionality.

**Key info :**
[![Docs](https://readthedocs.org/projects/pandas-openscm/badge/?version=latest)](https://pandas-openscm.readthedocs.io)
[![Main branch: supported Python versions](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Fopenscm%2Fpandas-openscm%2Fmain%2Fpyproject.toml)](https://github.com/openscm/pandas-openscm/blob/main/pyproject.toml)
[![Licence](https://img.shields.io/pypi/l/pandas-openscm?label=licence)](https://github.com/openscm/pandas-openscm/blob/main/LICENCE)

**PyPI :**
[![PyPI](https://img.shields.io/pypi/v/pandas-openscm.svg)](https://pypi.org/project/pandas-openscm/)
[![PyPI install](https://github.com/openscm/pandas-openscm/actions/workflows/install-pypi.yaml/badge.svg?branch=main)](https://github.com/openscm/pandas-openscm/actions/workflows/install-pypi.yaml)

**Conda :**
[![Conda](https://img.shields.io/conda/vn/conda-forge/pandas-openscm.svg)](https://anaconda.org/conda-forge/pandas-openscm)
[![Conda platforms](https://img.shields.io/conda/pn/conda-forge/pandas-openscm.svg)](https://anaconda.org/conda-forge/pandas-openscm)
[![Conda install](https://github.com/openscm/pandas-openscm/actions/workflows/install-conda.yaml/badge.svg?branch=main)](https://github.com/openscm/pandas-openscm/actions/workflows/install-conda.yaml)

**Tests :**
[![CI](https://github.com/openscm/pandas-openscm/actions/workflows/ci.yaml/badge.svg?branch=main)](https://github.com/openscm/pandas-openscm/actions/workflows/ci.yaml)
[![Coverage](https://codecov.io/gh/openscm/pandas-openscm/branch/main/graph/badge.svg)](https://codecov.io/gh/openscm/pandas-openscm)

**Other info :**
[![Last Commit](https://img.shields.io/github/last-commit/openscm/pandas-openscm.svg)](https://github.com/openscm/pandas-openscm/commits/main)
[![Contributors](https://img.shields.io/github/contributors/openscm/pandas-openscm.svg)](https://github.com/openscm/pandas-openscm/graphs/contributors)
## Status

<!---

We recommend having a status line in your repo
to tell anyone who stumbles on your repository where you're up to.
Some suggested options:

- prototype: the project is just starting up and the code is all prototype
- development: the project is actively being worked on
- finished: the project has achieved what it wanted
  and is no longer being worked on, we won't reply to any issues
- dormant: the project is no longer worked on
  but we might come back to it,
  if you have questions, feel free to raise an issue
- abandoned: this project is no longer worked on
  and we won't reply to any issues
-->

- prototype: the project is just starting up and the code is all prototype

<!--- --8<-- [end:description] -->

Full documentation can be found at:
[pandas-openscm.readthedocs.io](https://pandas-openscm.readthedocs.io/en/latest/).
We recommend reading the docs there because the internal documentation links
don't render correctly on GitHub's viewer.

## Installation

<!--- --8<-- [start:installation] -->
### As an application

If you want to use Pandas-OpenSCM as an application,
then we recommend using the 'locked' version of the package.
This version pins the version of all dependencies too,
which reduces the chance of installation issues
because of breaking updates to dependencies.

The locked version of Pandas-OpenSCM can be installed with

=== "mamba"
    ```sh
    mamba install -c conda-forge pandas-openscm-locked
    ```

=== "conda"
    ```sh
    conda install -c conda-forge pandas-openscm-locked
    ```

=== "pip"
    ```sh
    pip install 'pandas-openscm[locked]'
    ```

### As a library

If you want to use Pandas-OpenSCM as a library,
for example you want to use it
as a dependency in another package/application that you're building,
then we recommend installing the package with the commands below.
This method provides the loosest pins possible of all dependencies.
This gives you, the package/application developer,
as much freedom as possible to set the versions of different packages.
However, the tradeoff with this freedom is that you may install
incompatible versions of Pandas-OpenSCM's dependencies
(we cannot test all combinations of dependencies,
particularly ones which haven't been released yet!).
Hence, you may run into installation issues.
If you believe these are because of a problem in Pandas-OpenSCM,
please [raise an issue](https://github.com/openscm/pandas-openscm/issues).

The (non-locked) version of Pandas-OpenSCM can be installed with

=== "mamba"
    ```sh
    mamba install -c conda-forge pandas-openscm
    ```

=== "conda"
    ```sh
    conda install -c conda-forge pandas-openscm
    ```

=== "pip"
    ```sh
    pip install pandas-openscm
    ```

Additional dependencies can be installed using

=== "mamba"
    If you are installing with mamba, we recommend
    installing the extras by hand because there is no stable
    solution yet (see [conda issue #7502](https://github.com/conda/conda/issues/7502))

=== "conda"
    If you are installing with conda, we recommend
    installing the extras by hand because there is no stable
    solution yet (see [conda issue #7502](https://github.com/conda/conda/issues/7502))

=== "pip"
    ```sh
    # To add basic database dependencies
    pip install 'pandas-openscm[db]'

    # To add all database dependencies
    pip install 'pandas-openscm[db-full]'

    # To add plotting dependencies
    pip install 'pandas-openscm[plots]'

    # To add progress bar dependencies
    pip install 'pandas-openscm[progress]'

    # To add all optional dependencies
    pip install 'pandas-openscm[full]'
    ```

### For developers

For development, we rely on [uv](https://docs.astral.sh/uv/)
for all our dependency management.
To get started, you will need to make sure that uv is installed
([instructions here](https://docs.astral.sh/uv/getting-started/installation/)
(we found that the self-managed install was best,
particularly for upgrading uv later).

For all of our work, we use our `Makefile`.
You can read the instructions out and run the commands by hand if you wish,
but we generally discourage this because it can be error prone.
In order to create your environment, run `make virtual-environment`.

If there are any issues, the messages from the `Makefile` should guide you through.
If not, please raise an issue in the
[issue tracker](https://github.com/openscm/pandas-openscm/issues).

For the rest of our developer docs, please see [development][development].

<!--- --8<-- [end:installation] -->

## Original template

This project was generated from this template:
[copier core python repository](https://gitlab.com/openscm/copier-core-python-repository).
[copier](https://copier.readthedocs.io/en/stable/) is used to manage and
distribute this template.
