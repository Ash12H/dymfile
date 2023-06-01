# Contribute to the project

## Hooks

- Black
- Flake8

Use pre-commit before submitting Pull Request. ([link](https://ljvmiranda921.github.io/notebook/2018/06/21/precommits-using-black-and-flake8/)).

```bash
conda install pre-commit
pre-commit install
```

[**Sourcery**](https://sourcery.ai/) hooks are reserved for premium members, so they have not been added to this project. Nevertheless, it is strongly recommended to use sourcery review on the whole project and to follow the rules described in the [.sourcery.yaml](./.sourcery.yaml) file.

## Environment

Links [here](https://stackoverflow.com/questions/48787250/set-up-virtualenv-using-a-requirements-txt-generated-by-conda).

### Anaconda environment

To manage virtual environment with anaconda, use the `environment.yml` file as follow :

```bash
conda env create -f environment.yml
```

To export your environment use :

```bash
conda env export > environment.yml
```

You can also use the `requirement.txt` as follow :

```bash
conda create --name <env_name> --file requirements.txt
```

And if pip is installed on your conda environment you can export for pip user as follow :

```bash
pip freeze > requirements.txt
```

### Pip environment

Create your environment using `venv` :

```bash
python3 -m venv <env_name>
source ./<env_name>/bin/activate
```

To manage virtual environment with Pip, use the `requirement.txt` file as follow :

```bash
pip install -r requirements.txt
```

To export your environment use :

```bash
pip freeze > requirements.txt
```

## Install the project as a developper

> It is highly recommended to create a virtual environment first.

### Anaconda

Use the pip package include in the anaconda distribution.

### Pip

> Warning : Following command must be wrote at the project root.

Install :

```bash
pip install -e .
```

Uninstall :

```bash
pip uninstall .
```

## Scripts

Now you can call scripts like this :

```bash
python -m dymfiles.script.dymtonetcdf
```

## Test

You will need the `unittest` package to run unit test.

Documentation [here](https://docs.python.org/2/library/unittest.html#test-discovery).

```bash
python -m unittest discover

python -m unittest discover -s <directory>

python -m unittest discover -p <pattern> 
```
