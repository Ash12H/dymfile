# Install

## Simple installation

It is highly recommended to create a virtual environment first. See the [CONTRIBUTING.md](./CONTRIBUTING.md) file.

**WARNING** : Following command must be wrote at the project root.

### PIP

```bash
pip install .
```

### Anaconda

Use the pip command of your anaconda environment.

```bash
conda activate <my_environment>
pip install .
```

## Install the project as a developper

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
dymtonetcdf.py <...>
```
