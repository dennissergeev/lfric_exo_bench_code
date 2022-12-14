#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Quickplot functions for the UM output."""
import matplotlib.pyplot as plt
from aeolus.model import um
from aeolus.coord import get_cube_rel_days


def hcross(cube, ax=None, model=um, **kw_plt):
    newax = False
    if ax is None:
        ax = plt.axes()
        newax = True
    fig = ax.figure
    lons = cube.coord(um.x).points
    lats = cube.coord(um.y).points
    mappable = ax.pcolormesh(lons, lats, cube.data, **kw_plt)
    fig.colorbar(mappable, ax=ax)
    if newax:
        return ax


def timeseries_1d(cube, ax=None, model=um, **kw_plt):
    newax = False
    if ax is None:
        ax = plt.axes()
        newax = True
    days = get_cube_rel_days(cube, model=um)
    ax.plot(days, cube.data, **kw_plt)
    if newax:
        return ax


def timeseries_2d(cube, ax=None, model=um, **kw_plt):
    newax = False
    if ax is None:
        ax = plt.axes()
        newax = True
    fig = ax.figure
    days = get_cube_rel_days(cube, model=um)
    z = cube.coord(um.z).points
    mappable = ax.pcolormesh(days, z, cube.data.T, **kw_plt)
    fig.colorbar(mappable, ax=ax)
    if newax:
        return ax


def map_scatter(cube, ax=None, **kw_scatter):
    newax = False
    if ax is None:
        ax = plt.axes()
        newax = True
    fig = ax.figure
    # This doesn't work because lons and lats in the mesh are of size N+2
    # while the data array is of size N
    # lons, lats = cube.mesh.node_coords
    # lons, lats = lons.points, lats.points
    lons = cube.coord("longitude").points
    lats = cube.coord("latitude").points
    mappable = ax.scatter(lons, lats, c=cube.data, **kw_scatter)
    fig.colorbar(mappable, ax=ax)
    if newax:
        return ax
