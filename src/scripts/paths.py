# -*- coding: utf-8 -*-
"""Common paths useful for manipulating datasets and generating figures."""
from pathlib import Path

# Absolute path to the top level of the repository
root = Path(__file__).resolve().parents[2].absolute()

# Absolute path to the `src` folder
src = root / "src"

# Absolute path to the `src/static` folder (contains static images)
static = src / "static"

# Absolute path to the `src/scripts` folder (contains figure/pipeline scripts)
scripts = src / "scripts"

# Absolute path to the `src/figures` folder (contains figure output)
figures = src / "figures"

# Constants
const = scripts / "const"

# Absolute path to the `src/data` folder (contains datasets)
data_final = src / "data"
data = root.parent / "data"

# UM output
results_raw_um = data / "raw" / "um"
results_proc_um = data / "proc" / "um"

# LFRic output
results_raw_lfric = data / "raw" / "lfric"
results_proc_lfric = data / "proc" / "lfric"

# Vertical levels
# vert = data / "vert"
vert = data_final / "vert"
