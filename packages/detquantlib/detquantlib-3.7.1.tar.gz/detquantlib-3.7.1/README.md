# DET Quant Library

## Table of Contents

<!--TOC-->

- [DET Quant Library](#det-quant-library)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Exposed Symbols](#exposed-symbols)
    - [List of Exposed Symbols](#list-of-exposed-symbols)
  - [Configuration](#configuration)
    - [Project Structure](#project-structure)
    - [Dependencies](#dependencies)
      - [Dependency Manager](#dependency-manager)
      - [Dependabot](#dependabot)
    - [GitHub Actions](#github-actions)
      - [Workflow: Continuous Integration (CI)](#workflow-continuous-integration-ci)
        - [Invoke Tasks](#invoke-tasks)
        - [CI Check: Testing](#ci-check-testing)
        - [CI Check: Code Formatting](#ci-check-code-formatting)
      - [Workflow: Package Publisher](#workflow-package-publisher)
        - [Checking Version Updates](#checking-version-updates)
        - [Creating Version Tags](#creating-version-tags)
        - [Publishing Package Updates to PyPI](#publishing-package-updates-to-pypi)
    - [Release Notes](#release-notes)

<!--TOC-->

## Overview

The DET Quant Library is an internal library containing functions and classes that can be used
across Quant models.

## Exposed Symbols

Some of the package's symbols (i.e. functions, classes, modules, etc.) are exposed via
`__init__.py` files. They can therefore be imported with a more concise notation that does not
require specifying their full path.

This section references all exposed symbols, and for each one of them, provides an exhaustive
list of the ways they can be imported.

Note: The list below is auto-generated and can be udpated with the following command in the
terminal:

```cmd
poetry run python docs.py
```

### List of Exposed Symbols

<!-- START EXPOSED SYMBOLS AUTO-GENERATED -->

Classes:

- `DetDatabase`:
  - `from detquantlib.data import DetDatabase`
  - `from detquantlib.data.databases.detdatabase import DetDatabase`
- `Entsoe`:
  - `from detquantlib.data import Entsoe`
  - `from detquantlib.data.entsoe.entsoe import Entsoe`
- `OutputItem`:
  - `from detquantlib.outputs import OutputItem`
  - `from detquantlib.outputs.outputs_interface import OutputItem`
- `OutputSet`:
  - `from detquantlib.outputs import OutputSet`
  - `from detquantlib.outputs.outputs_interface import OutputSet`
- `PathDefinitions`:
  - `from detquantlib.outputs import PathDefinitions`
  - `from detquantlib.outputs.outputs_interface import PathDefinitions`
- `Sftp`:
  - `from detquantlib.data import Sftp`
  - `from detquantlib.data.sftp.sftp import Sftp`

<!-- END EXPOSED SYMBOLS AUTO-GENERATED -->

## Configuration

### Project Structure

The project mainly follows the standard Poetry structure:

```
detquantlib
├── pyproject.toml
├── README.md
├── detquantlib
│   └── __init__.py
└── tests
    └── __init__.py
```

### Dependencies

#### Dependency Manager

Project dependencies are managed by [Poetry](https://python-poetry.org/).

#### Dependabot

Automated dependency updates are executed with
[Dependabot](https://docs.github.com/en/code-security/dependabot).

### GitHub Actions

The project's CI/CD pipeline is enforced with [GitHub actions](https://docs.github.com/en/actions)
workflows.

#### Workflow: Continuous Integration (CI)

The continuous integration (CI) workflow runs tests to check the integrity of the codebase's
content, and linters to check the consistency of its format.

The workflow was inspired by the following preconfigured templates:

- [Python package](https://github.com/actions/starter-workflows/blob/main/ci/python-package.yml):
  A general workflow template for Python packages.
- [Poetry action](https://github.com/marketplace/actions/install-poetry-action): A GitHub action
  for installing and configuring Poetry.

##### Invoke Tasks

The workflow's checks and linters are specified with [Invoke](https://www.pyinvoke.org/) tasks,
defined in a tasks.py file.

Invoke tasks can be executed directly from the terminal, using the `inv` (or `invoke`)
command line tool.

For guidance on the available Invoke tasks, execute the following command in the terminal:

```cmd
inv --list
```

Use the `-h` (or `--help`) argument for help about a particular Invoke task. For example:

```cmd
inv lint -h
```

##### CI Check: Testing

Code changes are tested with the [Pytest](https://github.com/pytest-dev/pytest) package.

The CI check is executed with the following Invoke task:

```cmd
inv test -c
```

##### CI Check: Code Formatting

Linters are used to check that the code is properly formatted:

- [Isort](https://github.com/timothycrosley/isort) for the imports section
- [Darglint](https://github.com/terrencepreilly/darglint) for the docstrings description
- [Black](https://github.com/psf/black) for the main code
- [Pymarkdown](https://github.com/jackdewinter/pymarkdown) for the markdown file README.md

The CI check is executed with the following Invoke task:

```cmd
inv lint -c
```

If the CI check fails, execute the following command in the terminal:

```cmd
inv lint
```

This command fixes the parts of the code that should be reformatted. Adding the `-c` (or
`--check`) optional argument instructs the command to only _check_ if parts of the code should be
reformatted, without applying any actual changes.

#### Workflow: Package Publisher

The package publisher workflow checks the validity of package version updates, creates version
tags, and publishes package updates to PyPI.

##### Checking Version Updates

The workflow enforces version control:

- The version number is specified via the `version` field in the pyproject.toml file.
- The version number needs to be updated with every new master commit. If the version is not
  updated, the GitHub workflow will fail.
- Version numbers should follow semantic versioning (i.e. `X.Y.Z`). That is:
  - `X` increments represent major, non-backward compatible updates.
  - `Y` increments represent minor, backward compatible functionality updates.
  - `Z` increments represent patch/bugfix, backward compatible updates.

##### Creating Version Tags

If the new package version is valid, the workflow automatically creates a new tag for every new
master commit.

##### Publishing Package Updates to PyPI

The workflow automatically publishes every new master commit to
[PyPI](https://pypi.org/project/detquantlib/).

### Release Notes

When deemed necessary (especially in case of major updates), developers can document code
changes in dedicated GitHub release notes.

Release notes can be created via <https://github.com/Dynamic-Energy-Trading/detquantlib/releases.>

In any case, all codes changes should always be properly described/documented in GitHub issues
and/or pull requests.
