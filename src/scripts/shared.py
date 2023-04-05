#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Objects used by many scripts in the lfric_exo_bench project."""
# External modules
from aeolus.model import lfric, um

# Local modules
import paths


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
        "title": "LFRic-Atmosphere",
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
        "time_mean_period": 1000,
        "proc_fname_suffix": "sigma_p",
    },
    "el": {
        "title": "Earth-like",
        "short_title": "EL",
        "planet": "earth",
        "kw_plt": {"color": "C1"},
        "timestep": 1800,
        "time_mean_period": 1000,
        "proc_fname_suffix": "sigma_p",
    },
    "tle": {
        "title": "Tidally Locked Earth",
        "short_ztitle": "TLE",
        "planet": "tle",
        "kw_plt": {"color": "C2"},
        "timestep": 1800,
        "time_mean_period": 1000,
        "proc_fname_suffix": "sigma_p",
    },
}

THAI_CASES = {
    "thai_ben1": {
        "title": "Ben 1",
        "short_title": "Ben1",
        "planet": "ben1",
        "kw_plt": {"color": "C0"},
        "timestep": 1200,
        "time_mean_period": 610,
        "proc_fname_suffix": "regr",
    },
    "thai_ben2": {
        "title": "Ben 2",
        "short_title": "Ben2",
        "planet": "ben2",
        "kw_plt": {"color": "C1"},
        "timestep": 1200,
        "time_mean_period": 610,
        "proc_fname_suffix": "regr",
    },
    "thai_hab1": {
        "title": "Hab 1",
        "short_title": "Hab1",
        "planet": "hab1",
        "kw_plt": {"color": "C2"},
        "timestep": 1200,
        "time_mean_period": 610,
        "proc_fname_suffix": "regr",
    },
    "thai_hab2": {
        "title": "Hab 2",
        "short_title": "Hab2",
        "planet": "hab2",
        "kw_plt": {"color": "C3"},
        "timestep": 1200,
        "time_mean_period": 610,
        "proc_fname_suffix": "regr",
    },
}
