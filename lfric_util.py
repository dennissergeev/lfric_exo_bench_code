# -*- coding: utf-8 -*-
"""Utilities for LFRic output."""
import iris.exceptions
import iris.coords
import iris.util

import numpy as np


def fix_time_coord(cube, field, filename):
    """
    Callback function for `iris.load` specifically for UGRID data.

    All field variables should have time as a coord, and mesh variables
    will not have a time coord. So ignore anything that doesn't have a
    time coord. Note that mesh info will still be loaded in the
    coordinate part of the cube.

    Make sure that time coordinate is correct type, seems to always be
    loaded as a basic AuxCoord rather than a Scalar or DimCoord.
    """

    # Ignore cubes with no time coordinate
    if len(cube.coords("time")) == 0:
        raise iris.exceptions.IgnoreCubeException

    # Else, fix metadata in variables
    else:

        tcoord = cube.coord("time")

        # If only 1 time coordinate value, downgrade AuxCoord to Scalar
        if tcoord.points.size == 1:
            cube = cube.extract(iris.Constraint(time=tcoord.cell(0)))
        # Else, upgrade AuxCoord to DimCoord
        else:
            if isinstance(tcoord, iris.coords.AuxCoord):
                iris.util.promote_aux_coord_to_dim_coord(cube, tcoord)

    return cube


def add_equally_spaced_height_coord(cube, field, filename, model_top_height):
    """
    Callback function for `iris.load` specifically for LFRic data with vertical dimension.

    Adds a vertical coordinate of level heights assuming equally spaced levels.

    Examples
    --------
    >>> from functools import partial
    >>> iris.load(
        filename,
        callback=partial(add_equally_spaced_height_coord, model_top_height=32000)
    )
    """
    lev_coords = [i.name() for i in cube.dim_coords if i.name().endswith("_levels")]
    if len(lev_coords) == 1:
        lev_coord = cube.coord(lev_coords[0])
        if "full" in lev_coord.name().lower():
            points = np.linspace(0, model_top_height, lev_coord.shape[0])
        else:
            points = np.linspace(0, model_top_height, lev_coord.shape[0] + 1)
            points = 0.5 * (points[:-1] + points[1:])
        hgt_coord = iris.coords.AuxCoord(
            points, long_name="level_height", units="m", attributes=dict(positive="up")
        )
        hgt_coord.guess_bounds()
        cube.add_aux_coord(hgt_coord, data_dims=cube.coord_dims(lev_coord))

    return cube
