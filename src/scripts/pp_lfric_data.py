#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Process LFRic output by interpolating selected fields to a common grid."""

# Commonly used standard library tools
import argparse
from functools import partial
from pathlib import Path
from time import time
import warnings

# Scientific library
import iris
from iris.experimental.ugrid import PARSE_UGRID_ON_LOAD

# My packages and local scripts
from aeolus.const import add_planet_conf_to_cubes, init_const
from aeolus.coord import get_cube_rel_days
from aeolus.io import save_cubelist, create_dummy_cube
from aeolus.subset import unique_cubes
import paths

from pouch.log import create_logger

from lfric_util import (
    add_equally_spaced_height_coord,
    simple_regrid_lfric,
    add_um_height_coord,
)

# Global definitions and styles
warnings.filterwarnings("ignore")
SCRIPT = Path(__file__).name


def parse_args(args=None):
    """Argument parser."""
    ap = argparse.ArgumentParser(
        SCRIPT,
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog=f"""Usage:
./{SCRIPT} -p earth -l trap1e -i ~/path/to/inp/dir/ -o ~/path/to/out/dir
""",
    )

    ap.add_argument("-i", "--inpdir", type=str, help="Input directory")
    ap.add_argument("-o", "--outdir", type=str, help="Output directory")
    ap.add_argument(
        "-l", "--label", type=str, required=True, help="Simulation label"
    )
    ap.add_argument(
        "-p", "--planet", type=str, required=True, help="Planet configuration"
    )
    ap.add_argument(
        "-c",
        "--cnum",
        type=str,
        help="Cubed Sphere Mesh Number",
        default="C48",
    )
    ap.add_argument(
        "--ref_cube",
        type=str,
        default="air_potential_temperature",
        help="Reference cube, to which coordinates all data will be regridded",
    )
    ap.add_argument(
        "--level_height",
        type=str,
        default="uniform",
        help="Type of the vertical level height coordinate",
    )
    return ap.parse_args(args)


def main(args=None):
    """Main entry point of the script."""
    t0 = time()
    L = create_logger(Path(__file__))
    # Parse command-line arguments
    args = parse_args(args)
    planet = args.planet
    L.info(f"{planet=}")

    label = args.label
    L.info(f"{label=}")

    # Cubed sphere mesh C number
    c_num = args.cnum

    # Height coordinate
    if args.level_height == "uniform":
        add_levs = partial(
            add_equally_spaced_height_coord, model_top_height=32_000
        )
    elif args.level_height == "um_L38_29t_9s_40km":
        add_levs = partial(
            add_um_height_coord,
            path_to_levels_file=paths.vert / "vertlevs_L38_29t_9s_40km",
        )
    else:
        raise ValueError(f"level_height={args.level_height} is not valid.")

    # Input directory
    # inpdir = mypaths.sadir / label
    inpdir = Path(args.inpdir)
    L.info(f"{inpdir=}")

    # Create a subdirectory for processed data
    outdir = Path(args.outdir)
    # outdir = mypaths.sadir / label / "_processed"
    outdir.mkdir(parents=True, exist_ok=True)

    # Make a list of files matching the file mask and the start day threshold
    fnames = sorted(
        inpdir.glob(f"*/*{c_num}*/lfric_diag.nc"),
        key=lambda x: int(x.parent.parent.name),
    )
    if len(fnames) == 0:
        L.critical("No files found!")
        return
    L.info(f"fnames({len(fnames)}) = {fnames[0]} ... {fnames[-1]}")

    with PARSE_UGRID_ON_LOAD.context():
        cl_raw = iris.load(
            fnames,
            callback=add_levs,
        )

        for cube in cl_raw:
            try:
                cube.attributes.pop("timeStamp")
                cube.attributes.pop("uuid")
            except KeyError:
                pass
        cl_raw = cl_raw.concatenate(check_aux_coords=False)

        if len(cl_raw) == 0:
            L.critical("Files are empty!")
            return
    # L.info(f"{cl_raw=}")
    cubes_to_regrid = cl_raw.extract(
        [
            # "rho",
            # "theta",
            "pmsl",
            "temperature",
            # "tot_col_int_energy",
            # "tot_col_dry_air_mass",
            # "tot_col_pot_energy",
            # "divergence",
            # "u_in_w2h",
            # "v_in_w2h",
            "u_in_w3",
            "v_in_w3",
            "w_in_wth",
            # "exner",
            # "exner_in_wth",
            "grid_surface_temperature",
            "pressure_in_wth",
            "sw_direct_toa",
            "sw_up_toa",
            "lw_up_toa",
        ]
    )
    cubes_to_regrid = unique_cubes(cubes_to_regrid)
    if len(w_cubes := cubes_to_regrid.extract("w_in_wth")) == 2:
        cubes_to_regrid.remove(w_cubes[-1])
    for cube in cubes_to_regrid:
        if cube.units == "ms-1":
            cube.units = "m s-1"
    # L.info(f"{cubes_to_regrid=}")
    # Create a dummy cube with a target grid
    tgt_cube = create_dummy_cube(nlat=90, nlon=144, pm180=True)
    # Regrid all cubes
    cl_proc = simple_regrid_lfric(
        cubes_to_regrid, tgt_cube=tgt_cube, ref_cube_constr=args.ref_cube
    )
    const = init_const(planet, directory=paths.const)
    add_planet_conf_to_cubes(cl_proc, const=const)

    time_prof = "inst"
    # Write the data to a netCDF file
    gl_attrs = {
        "name": label,
        "planet": planet,
        "processed": "True",
    }
    days = 0 + get_cube_rel_days(cl_proc[0]).astype(int)
    day_str = f"days{days[0]}"
    if len(days) > 1:
        day_str += f"_{days[-1]}"
    fname_out = outdir / f"{label}_{time_prof}_{day_str}.nc"
    save_cubelist(cl_proc, fname_out, **gl_attrs)
    L.success(f"Saved to {fname_out}")
    L.info(f"Execution time: {time() - t0:.1f}s")


if __name__ == "__main__":
    main()
