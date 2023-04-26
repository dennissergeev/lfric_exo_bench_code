#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Average post-processed data in time and save as a netCDF file."""
import warnings
from datetime import datetime

# External modules
import iris
from aeolus.calc import last_n_day_mean
from aeolus.io import load_data, save_cubelist
from tqdm import tqdm

# Local modules
import paths
from shared import MODELS, TF_CASES, THAI_CASES

# Ignore warnings about time coordinate bounds
warnings.filterwarnings("ignore")

# Define global attributes of the output file
GLOBAL_ATTRS = {
    "summary": "Model data for Sergeev et al. (egusphere-2023-647)",
    "conventions": "CF-1.7,ACDD-1.3",
    "creator_name": "Denis Sergeev",
    "creator_email": "d.sergeev@exeter.ac.uk",
    "creator_institution": "University of Exeter",
    "project": "Exascale Exoplanet Modelling",
    "coverage_content_type": "modelResult",
}

# Combine all experiments into one dictionary
SIM_CASES = {**TF_CASES, **THAI_CASES}

# Loop over models (UM, LFRic)
for model_key, model_prop in tqdm(MODELS.items()):
    if model_key != "lfric":
        continue
    model = model_prop["model"]

    # Loop over experiments
    for sim_label, sim_prop in tqdm(SIM_CASES.items(), leave=False):
        fname_mask = f"{sim_label}*{sim_prop['proc_fname_suffix']}.nc"
        dset = load_data(
            sorted((model_prop["data_proc_path"] / sim_label).glob(fname_mask))
        )
        # Average each cube in time and append them to a new cube list
        dset_tm = iris.cube.CubeList()
        for cube in dset:
            dset_tm.append(
                last_n_day_mean(
                    cube, days=sim_prop["time_mean_period"], model=model
                )
            )
        # Define and create a new data directory
        outdir = paths.data_final / model_key / sim_label
        outdir.mkdir(parents=True, exist_ok=True)
        fname_out = (
            outdir
            / f"{sim_label}_{sim_prop['proc_fname_suffix']}_time_mean.nc"
        )
        # Update global attributes to insert the name of the model
        GLOBAL_ATTRS["title"] = f"Model Output from {model_prop['title']}"
        GLOBAL_ATTRS[
            "date_created"
        ] = f"{datetime.utcnow():%Y-%m-%d %H:%M:%S} GMT"
        # Save the result
        save_cubelist(dset_tm, fname_out, **GLOBAL_ATTRS)
