# Setting up a development environment

1. Install Python 3.10 or 3.11
2. Install poetry - see [the poetry docs](https://python-poetry.org/docs/)
3. Run `poetry install --extras azure` to install the project's dependencies

# Running the CI lints locally

See [linting.yml](.github/workflows/linting.yml) for the list of linting commands run by the CI on Github,
such as:

`poetry run ruff .`
`poetry run black --check .`
`poetry run mypy .`
