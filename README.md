<h1 align="center">
Simulations of idealised 3D atmospheric flows on terrestrial planets using LFRic-Atmosphere
</h1>
<h4 align="center">Submitted to GMD</h4>

<p align="center">
  <img src="https://img.shields.io/badge/wip-%20%F0%9F%9A%A7%20under%20review%20%F0%9F%9A%A7-yellow"
       alt="wip">
</p>

<p align="center">
<a href="https://www.python.org/downloads/">
<img src="https://img.shields.io/badge/python-3.11-blue.svg"
     alt="Python 3.11"></a>
<a href="https://github.com/psf/black">
<img src="https://img.shields.io/badge/code%20style-black-000000.svg"
     alt="black"></a>
<a href="LICENSE">
<img src="https://img.shields.io/badge/license-MIT-green.svg"
     alt="License: MIT"></a>
<a href="https://zenodo.org/badge/latestdoi/434663522">
<img src="https://zenodo.org/badge/434663522.svg"
     alt="DOI"></a>
</p>


<h2 align="center">Repository contents</h2>

Notebooks and Python scripts are in the [`src/scripts/` directory](src/scripts/), while the figures themselves are in the `src/figures/` directory.
The final regridded and time mean data are in the `src/data/` directory.

|  #  | Figure or Table | Notebook |
|:---:|:----------------|:---------|
|  1  | [3D image of the cubed sphere mesh]() | [Mesh-3D.ipynb](https://nbviewer.jupyter.org/github/dennissergeev/lfric_exo_bench_code/blob/main/src/scripts/Mesh-3D.ipynb) |
|  2  | [Conservation diagnostics in the Temperature Forcing cases]() | [Conservation-Diags.ipynb](https://nbviewer.jupyter.org/github/dennissergeev/lfric_exo_bench_code/blob/main/src/scripts/Conservation-Diags.ipynb) |
|  3  | [Temperature Forcing climate]() | [External-Forcing-Plots.ipynb](https://nbviewer.jupyter.org/github/dennissergeev/lfric_exo_bench_code/blob/main/src/scripts/External-Forcing-Plots.ipynb) |
|  4  | [Mean climate in the THAI cases]() | [THAI-Plots.ipynb](https://nbviewer.jupyter.org/github/dennissergeev/lfric_exo_bench_code/blob/main/src/scripts/THAI-Plots.ipynb) |
|  5  | [Global mean climate diagnostics table]() | [Tab04-THAI-Global-Diags.ipynb](https://nbviewer.jupyter.org/github/dennissergeev/lfric_exo_bench_code/blob/main/src/scripts/Tab04-THAI-Global-Diags.ipynb) |

<h2 align="center">How to reproduce figures</h2>

<h3 align="center">Set up environment</h3>

To recreate the required environment for running Python code, follow these steps. (Skip the first two steps if you have Jupyter Lab with `nb_conda_kernels` installed already.)

1. Install mamba, e.g. using [mambaforge](https://github.com/conda-forge/miniforge#mambaforge).
2. Install necessary packages to the `base` environment. Make sure you are installing them from the `conda-forge` channel.
```bash
mamba install -c conda-forge jupyterlab nb_conda_kernels
```
3. Git-clone or download this repository to your computer.
4. In the command line, navigate to the downloaded folder, e.g.
```bash
cd /path/to/downloaded/repository
```
5. Create a separate conda environment (it will be called `lfric_ana`).
```
mamba env create --file environment.yml
```

<h3 align="center">Open the code</h3>

1. Start the Jupyter Lab, for example from the command line (from the `base` environment).
```bash
jupyter lab
```
2. Open noteboks in the `lfric_ana` environment and run them.


<h2 align="center">
System information and key python libraries
</h2>

```
--------------------------------------------------------------------------------
  Date: Wed Apr 05 12:42:43 2023 UTC

                OS : Linux
            CPU(s) : 192
           Machine : x86_64
      Architecture : 64bit
               RAM : 503.5 GiB
       Environment : Python
       File system : ext4

  Python 3.11.2 | packaged by conda-forge | (main, Mar 31 2023, 17:51:05) [GCC
  11.3.0]

            aeolus : 0.4.16+15.gd4237f3
              dask : 2023.3.2
       esmf_regrid : 0.6.0
              iris : 3.4.1
        matplotlib : 3.7.1
             numpy : 1.24.2
          stratify : 0.2.post0
--------------------------------------------------------------------------------
```
