# -*- coding: utf-8 -*-
"""Paths to data."""
from pathlib import Path

# Top-level directory containing code and data (one level up)
top = Path(__file__).absolute().parent.parent

# Plotting output
plot = top / "plots"
plot.mkdir(parents=True, exist_ok=True)

# Constants
const = Path(__file__).absolute().parent / "const"

# UM 
# Modelling results
results_um = top.parent / "modelling" / "um" / "results" / "sa"
# Start dumps
start_dumps_um = top.parent / "modelling" / "um" / "start_dumps"
# Vertical levels
vert_um = top.parent / "modelling" / "um" / "vert"

# LFRic
# Modelling results
results_lfric = top.parent / "modelling" / "lfric" / "results"
# Start dumps
start_dumps_lfric = top.parent / "modelling" / "lfric" / "start_dumps"