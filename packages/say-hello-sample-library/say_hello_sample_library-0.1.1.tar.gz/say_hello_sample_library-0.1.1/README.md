# Say Hello!

<p align="center">
  <img src="https://cdn.charly-ginevra.fr/say-hello-sample-library/logo.png" width="250" alt="Say Hello! Logo" />
</p>
<p align="center">Sample Python Package using UV</p>
<p align="center">
  <a href="https://www.python.org/" target="_blank"><img src="https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=fff" alt="Python" /></a>
  <a href="https://pypi.org/" target="_blank"><img src="https://img.shields.io/badge/PyPI-3775A9?logo=pypi&logoColor=fff" alt="PyPi" /></a>
</p>

## Get Start

1. You need to have UV installed. You can find instructions [here](https://docs.astral.sh/uv/getting-started/installation/).

2. Create the virtual environment
```bash
uv venv # create env .venv
uv sync # install dependencies
```

3. Develop your lib in `src` and tests in `test`.

4. In order to commit you need to :
    + Have no error from linter ([ruff](https://docs.astral.sh/ruff/))
    + Pass all tests ([pytest](https://docs.pytest.org/en/stable/))

5. Push

## Test

Tests must be write in `tests` and follow the convention of [pytest](https://docs.pytest.org/en/stable/)

## Code Quality

To ensure a certain level of code quality, Ruff is used.

You can find the configuration in `pyproject.toml`.

## Scripts

`noxfile.py`

+ `lint` :
+ `clean` :
+ `test` :

## Publish your package

You package is published automaticly after a push on `dev` or `main`.

> A push on `dev` will publish your package on https://test.pypi.org/

You can also publish it manually with the following commands :
```bash
uv publish --index testpypi --token YOUR_PYPI_TOKEN
# OR
uv publish --index testpypi --token YOUR_PYPI_TOKEN
```