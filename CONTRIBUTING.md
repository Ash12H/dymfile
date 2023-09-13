# Contribute to the project

## Hooks

- Ruff
- Black

Use pre-commit before submitting Pull Request. ([link](https://ljvmiranda921.github.io/notebook/2018/06/21/precommits-using-black-and-flake8/)).

```bash
pip install pre-commit
pre-commit install
```

[**Sourcery**](https://sourcery.ai/) hooks are reserved for premium members, so they have not been added to this project. Nevertheless, it is strongly recommended to use sourcery review on the whole project and to follow the rules described in the [.sourcery.yaml](./.sourcery.yaml) file.

## Environment

Links [here](https://stackoverflow.com/questions/48787250/set-up-virtualenv-using-a-requirements-txt-generated-by-conda).

### Anaconda environment

Export :

```bash
conda env export --no-builds > environment.yml
```

### Pip environment

Create your environment using `venv` :

```bash
python3 -m venv .venv
source ./.venv/bin/activate
```

To manage virtual environment with Pip, use the `requirement.txt` file as follow :

```bash
pip install -r requirements.txt
```

To install Dymfile library :

```bash
pip install -e .
```

To export your environment use :

```bash
pip list --format=freeze > requirements.txt
```

## Test

You will need the `unittest` package to run unit test.

Documentation [here](https://docs.python.org/2/library/unittest.html#test-discovery).

```bash
python -m unittest discover

python -m unittest discover -s <directory>

python -m unittest discover -p <pattern> 
```

## Run scripts

Example :

```bash
dymtonetcdf.py <args>
```
