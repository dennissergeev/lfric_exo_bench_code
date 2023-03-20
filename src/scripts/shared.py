#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Objects used by many scripts in the lfric_exo_bench project."""
# Standard library
from pathlib import Path
from typing import Sequence, Union

# External modules
from aeolus.model import um
import iris
from iris.cube import CubeList

# Local modules
import paths
from lfric_model import lfric


MODELS = {
    "um": {
        "model": um,
        "results_path": paths.results_proc_um,
        "title": "UM",
        "kw_plt": {
            "linestyle": "--",
            "linewidth": 0.75,
            "dash_capstyle": "round",
        },
    },
    "lfric": {
        "model": lfric,
        "results_path": paths.results_proc_lfric,
        "title": "LFRic",
        "kw_plt": {"linestyle": "-", "linewidth": 1.25},
    },
}


TF_CASES = {
    "hs": {
        "title": "Held-Suarez",
        "short_title": "HS",
        "planet": "earth",
        "kw_plt": {"color": "C0"},
        "timestep": 1800,
    },
    "el": {
        "title": "Earth-like",
        "short_title": "EL",
        "planet": "earth",
        "kw_plt": {"color": "C1"},
        "timestep": 1800,
    },
    "tle": {
        "title": "Tidally Locked Earth",
        "short_ztitle": "TLE",
        "planet": "tle",
        "kw_plt": {"color": "C2"},
        "timestep": 1800,
    },
    # "tle_dlayer_off": {
    #     "title": "Tidally Locked Earth dlayer OFF",
    #     "short_title": "TLE dlayer OFF",
    #     "planet": "tle",
    #     "kw_plt": {"color": "C2"},
    #     "timestep": 1800,
    # },
    # "tle_dl_type_standard": {
    #     "title": "Tidally Locked Earth dl_type standard",
    #     "short_title": "TLE dlayer OFF",
    #     "planet": "tle",
    #     "kw_plt": {"color": "C2"},
    #     "timestep": 1800,
    # },
}


def load_proc_data(fnames: Sequence[Union[Path, str]]) -> CubeList:
    """Load post-processed data."""
    with iris.FUTURE.context(datum_support=True):
        dset = iris.load(fnames)
    return dset
