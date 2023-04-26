#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Interpolate processed UM or LFRic output to sigma-p surfaces."""

# Commonly used standard library tools
import argparse
from functools import partial
from pathlib import Path
from time import time

# External modules
from aeolus.const import init_const
from aeolus.io import load_data, save_cubelist
from aeolus.model import lfric
from aeolus.calc import calc_derived_cubes
from aeolus.log import create_logger
import iris
from iris.experimental import stratify
import numpy as np

# Local modules
import paths
from shared import MODELS

# Global definitions and styles
# Self name
SCRIPT = Path(__file__).name
# Create a callable to pass to the interpolation routine.
# Use linear extrapolation.
INTERPOLATOR = partial(
    stratify.stratify.interpolate,
    interpolation=stratify.stratify.INTERPOLATE_LINEAR,
    extrapolation=stratify.stratify.EXTRAPOLATE_LINEAR,
)
# Create an array of $\sigma_p=p/p_s$ levels,
# close to the table A1 in Mayne et al. (2014).
SIGMA_LEVELS = np.linspace(1, 0.01, 34)


def parse_args(args=None):
    """Argument parser."""
    ap = argparse.ArgumentParser(
        SCRIPT,
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog=f"""Usage:
./{SCRIPT} -m lfric -i ~/path/to/inp/dir/ [-o ~/path/to/out/dir]
""",
    )

    ap.add_argument(
        "-m",
        "--model",
        type=str,
        required=True,
        help="Model",
        choices=["um", "lfric"],
    )
    ap.add_argument(
        "-i", "--inpdir", type=str, help="Input directory", required=True
    )
    ap.add_argument("-o", "--outdir", type=str, help="Output directory")
    return ap.parse_args(args)


def main(args=None):
    """Main entry point of the script."""
    t0 = time()
    L = create_logger(Path(__file__))
    # Parse command-line arguments
    args = parse_args(args)
    model_key = args.model
    L.info(f"{model_key=}")
    model = MODELS[model_key]["model"]

    # Input directory
    inpdir = Path(args.inpdir)

    if outdir := args.outdir:
        # If given, create a subdirectory for processed data
        outdir = Path(args.outdir)
        outdir.mkdir(parents=True, exist_ok=True)
        L.info(f"{inpdir=}")
        L.info(f"{outdir=}")
    else:
        outdir = inpdir
        L.info(f"inpdir=outdir={inpdir}")

    # Get the input file
    try:
        fname = sorted(
            i
            for i in inpdir.glob("*.nc")
            if ("_sigma_p" not in i.stem) and ("conservation" not in i.stem)
        )[
            0
        ]  # Assume only 1 file
    except IndexError:
        L.critical("No file found")

    L.info(f"{fname=}")
    dset = load_data(fname)
    if len(dset) == 0:
        L.critical("The file is empty")
        return
    planet = dset[0].attributes["planet"]

    const = init_const(planet, directory=paths.const)
    calc_derived_cubes(dset, const=const, model=model)

    # Interpolation / relevelling
    dset_interp = iris.cube.CubeList()
    pres = dset.extract_cube(model.pres)
    p_sfc = pres.extract(iris.Constraint(**{model.z: 0}))
    sigma_p = pres / p_sfc
    sigma_p.rename(lfric.s)

    for cube in dset.extract(
        [model.temp, model.u, model.v, model.w, model.pres, model.dens]
    ):
        dset_interp.append(
            stratify.relevel(
                cube,
                sigma_p,
                SIGMA_LEVELS,
                axis=model.z,
                interpolator=INTERPOLATOR,
            )
        )

    # Write the data to a netCDF file
    fname_out = fname.with_stem(f"{fname.stem}_sigma_p")
    save_cubelist(dset_interp, fname_out)
    L.success(f"Saved to {fname_out}")
    L.info(f"Execution time: {time() - t0:.1f}s")


if __name__ == "__main__":
    main()
