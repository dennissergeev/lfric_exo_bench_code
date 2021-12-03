[![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-black.svg)](LICENSE)
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

:warning: **Work in progress** :warning:

# LFRic THAI 
THAI simulations in LFRic

## Setting up
1. Install [Mambaforge](https://github.com/conda-forge/miniforge#mambaforge).
2. Install `jupyter lab` and `nb_conda_kernels` into your `base` environment.
```bash
mamba install jupyterlab nodejs nb_conda_kernels
```
3. Download or `git clone` this repository.
4. In the command line, navigate to the local copy of this repository and type
```bash
mamba env create --file=environment.yml
```

## Updating the environment
If upstream dependencies have been changed, you can update the existing environment by running
```bash
mamba env update --file=environment.yml
```
