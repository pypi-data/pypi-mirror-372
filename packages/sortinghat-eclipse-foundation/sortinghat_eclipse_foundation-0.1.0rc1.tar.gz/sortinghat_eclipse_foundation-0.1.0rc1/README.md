# sortinghat-eclipse-foundation

SortingHat backend to import identities from Eclipse Foundation

## Requirements

 - Python >= 3.9

You will also need some other libraries for running the tool, you can find the
whole list of dependencies in [pyproject.toml](pyproject.toml) file.

## Installation

There are several ways to install sortinghat-eclipse-foundation on your system: packages or source
code using Poetry or pip.

### PyPI

sortinghat-eclipse-foundation can be installed using pip, a tool for installing Python packages.
To do it, run the next command:
```
$ pip install sortinghat-eclipse-foundation
```

### Source code

To install from the source code you will need to clone the repository first:
```
$ git clone https://github.com/bitergia-analytics/sortinghat-eclipse-foundation
$ cd sortinghat-eclipse-foundation
```

Then use pip or Poetry to install the package along with its dependencies.

#### Pip

To install the package from local directory run the following command:
```
$ pip install .
```
In case you are a developer, you should install sortinghat-eclipse-foundation in editable mode:
```
$ pip install -e .
```

#### Poetry

We use [poetry](https://python-poetry.org/) for dependency management and
packaging. You can install it following its [documentation](https://python-poetry.org/docs/#installation).
Once you have installed it, you can install sortinghat-openinfra and the dependencies in
a project isolated environment using:
```
$ poetry install
```
To spaw a new shell within the virtual environment use:
```
$ poetry shell
```

## Usage

Install this SortingHat backend to import identities from the Eclipse Foundation.
You can use this importer using the API or the UI. The name of the backend is
`EclipseFoundation`. You will have to provide the credentials on the settings file
in order to access the Eclipse Foundation API:

- `ECLIPSE_FOUNDATION_USER_ID`: username on the Eclipse Foundation platform.
- `ECLIPSE_FOUNDATION_PASSWORD`: password for the previous user.

The user will also have the next permissions for reading the identities:

- `eclipsefdn_view_all_profiles`
