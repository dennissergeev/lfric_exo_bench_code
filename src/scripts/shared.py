#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Objects used by many scripts in the lfric_exo_bench project."""
# Standard library
from pathlib import Path
from typing import Sequence, Union
import math
from typing import Optional


# External modules
from aeolus.model import um
from aeolus.plot import unit_format

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
}


def load_proc_data(fnames: Sequence[Union[Path, str]]) -> CubeList:
    """Load post-processed data."""
    with iris.FUTURE.context(datum_support=True):
        dset = iris.load(fnames)
    return dset


def cube_minmeanmax_nonweighted_str(
    cube: iris.cube.Cube,
    sep: Optional[str] = " | ",
    eq_sign: Optional[str] = "=",
    fmt: Optional[str] = "auto",
    **kw_unit_format,
):
    """Return min, mean and max of an iris cube as a string."""
    # Compute the stats
    _min = float(cube.data.min())
    _mean = float(cube.data.mean())
    _max = float(cube.data.max())
    # Assemble a string
    txts = []
    for label, num in zip(["min", "mean", "max"], [_min, _mean, _max]):
        if fmt == "auto":
            if (math.log10(abs(_mean)) < 0) or (math.log10(abs(_mean)) > 5):
                _str = f"{label}{eq_sign}{num:.0e}"
            else:
                _str = f"{label}{eq_sign}{round(num):.0f}"
        elif fmt == "pretty":
            _str = f"{label}{eq_sign}{unit_format(num, **kw_unit_format)}"
        else:
            _str = f"{label}{eq_sign}{num:{fmt}}"
        txts.append(_str)
    return sep.join(txts)
