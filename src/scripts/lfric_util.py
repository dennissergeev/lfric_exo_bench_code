# -*- coding: utf-8 -*-
"""Utilities for LFRic output."""
import iris.exceptions
import iris.coords
import iris.util

import numpy as np

from aeolus.model import um
from esmf_regrid.experimental.unstructured_scheme import (
    MeshToGridESMFRegridder,
)


def add_equally_spaced_height_coord(cube, field, filename, model_top_height):
    """
    Callback for `iris.load` specifically for LFRic data with vertical coord.

    Adds a vertical coordinate of level heights assuming equally spaced levels.

    Examples
    --------
    >>> from functools import partial
    >>> iris.load(
        filename,
        callback=partial(
            add_equally_spaced_height_coord,
            model_top_height=32000
        )
    )
    """
    lev_coords = [
        i.name() for i in cube.dim_coords if i.name().endswith("_levels")
    ]
    if len(lev_coords) == 1:
        lev_coord = cube.coord(lev_coords[0])
        if "full" in lev_coord.name().lower():
            points = np.linspace(0, model_top_height, lev_coord.shape[0])
        else:
            points = np.linspace(0, model_top_height, lev_coord.shape[0] + 1)
            points = 0.5 * (points[:-1] + points[1:])
        hgt_coord = iris.coords.AuxCoord(
            points,
            long_name="level_height",
            units="m",
            attributes=dict(positive="up"),
        )
        hgt_coord.guess_bounds()
        cube.add_aux_coord(hgt_coord, data_dims=cube.coord_dims(lev_coord))

    return cube


def clean_attrs(cube, field, filename):
    """
    Callback for `iris.load` to clean up trivial attributes in LFRic data.

    Needed for concatenating cubes.
    """
    try:
        cube.attributes.pop("timeStamp")
        cube.attributes.pop("uuid")
    except KeyError:
        pass

    return cube


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


def replace_level_coord_with_height(cube):
    """
    Remove full_ or half_levels coordinate and replace it with level_height.

    Assumes that the cube contains level_height already.

    See Also
    --------
    add_equally_spaced_height_coord
    """
    lev_coords = [
        i.name() for i in cube.dim_coords if i.name().endswith("_levels")
    ]
    if len(lev_coords) == 1:
        lev_coord = cube.coord(lev_coords[0])
        cube.remove_coord(lev_coord)
        iris.util.promote_aux_coord_to_dim_coord(cube, "level_height")
    return cube


def _regrid_cubes_on_edges(src_cube, tgt_cube, method="auto"):
    """Temporary solution to regrid cubes defined on cell edges."""
    # Using the approach in gungho/rose-stem/app/plot/bin/plot_zonal.py
    from iris._concatenate import _CubeSignature
    from iris.analysis.cartography import get_xy_grids
    from scipy.interpolate import griddata

    src_x = src_cube.coord("longitude").points
    src_y = src_cube.coord("latitude").points
    tgt_x2d, tgt_y2d = get_xy_grids(tgt_cube)

    non_xy_coords = [
        name
        for c in src_cube.dim_coords
        if (name := c.name()) not in ["longitude", "latitude"]
    ]

    result = iris.cube.CubeList()
    for src_2d_slice in src_cube.slices_over(non_xy_coords):
        # Interpolate using delaunay triangularization
        if method == "auto":
            reg_data_linear = griddata(
                (src_x, src_y),
                src_2d_slice.data,
                (tgt_x2d, tgt_y2d),
                method="linear",
            )
            reg_data_nearest = griddata(
                (src_x, src_y),
                src_2d_slice.data,
                (tgt_x2d, tgt_y2d),
                method="nearest",
            )
            reg_data_linear[np.isnan(reg_data_linear)] = reg_data_nearest[
                np.isnan(reg_data_linear)
            ]
            reg_data = reg_data_linear
        else:
            reg_data = griddata(
                (src_x, src_y),
                src_2d_slice.data,
                (tgt_x2d, tgt_y2d),
                method=method,
            )
        reg_cube_slice = tgt_cube.copy(data=reg_data)
        for scalar_coord in _CubeSignature(src_2d_slice).scalar_coords:
            reg_cube_slice.add_aux_coord(scalar_coord)
        result.append(reg_cube_slice)
    result = result.merge_cube()
    dim_order = [*range(src_cube.ndim + 1)]
    dim_order[0], dim_order[1] = 1, 0
    result.transpose(dim_order)
    result.metadata = src_cube.metadata
    return result


def simple_regrid_lfric(
    cube_list, tgt_cube, ref_cube_constr="air_potential_temperature"
):
    """Quick&dirty regridding of LFRic data to a common height/lat/lon grid."""
    # Horizontal regridding
    result_h = iris.cube.CubeList()
    ref_cube = cube_list.extract_cube(ref_cube_constr)
    regridder = MeshToGridESMFRegridder(
        ref_cube, tgt_cube, method="conservative"
    )
    for cube in cube_list:
        if cube.location == "edge":
            cube_reg = _regrid_cubes_on_edges(cube, tgt_cube)
        else:
            cube_reg = regridder(cube)
        result_h.append(cube_reg)
    # Vertical interpolation
    result_v = iris.cube.CubeList()
    tgt_points = ("level_height", ref_cube.coord("level_height").points)
    for cube in result_h:
        if len(
            [i.name() for i in cube.dim_coords if i.name().endswith("_levels")]
        ):
            result_v.append(
                replace_level_coord_with_height(cube).interpolate(
                    [tgt_points], iris.analysis.Linear()
                )
            )
        else:
            result_v.append(cube)
    return result_v


def ugrid_spatial(cube, aggr, model=um):
    cube_copy = cube.copy()
    tmp_coord = iris.coords.AuxCoord(
        points=np.arange(cube.coord(model.x).shape[0]),
        long_name="mesh_coordinates",
    )

    cube_copy.add_aux_coord(tmp_coord, data_dims=cube.coord_dims(model.x))

    cube_copy.remove_coord(model.x)
    cube_copy.remove_coord(model.y)

    cube_aggr = cube_copy.collapsed(
        tmp_coord.name(), getattr(iris.analysis, aggr.upper())
    )
    cube_aggr.remove_coord(tmp_coord)
    return cube_aggr


def ugrid_spatial_mean(cube, model=um):
    return ugrid_spatial(cube, "mean", model=model)
