#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Process global UM output by interpolating selected fields to common grid."""

# Commonly used standard library tools
import argparse
from pathlib import Path
from time import time
import warnings

# My packages and local scripts
from aeolus.const import add_planet_conf_to_cubes, init_const
from aeolus.coord import get_cube_rel_days
from aeolus.io import load_data, save_cubelist
from aeolus.model import um
import paths

from pouch.log import create_logger
from pouch.proc_um_output import get_filename_list, process_cubes

# Global definitions and styles
warnings.filterwarnings("ignore")
SCRIPT = Path(__file__).name
DEFAULT_REGEX = r"{1}[0]{6}(?P<timestamp>[0-9]{2,6})_00"

GLM_MODEL_TIMESTEP = 1200
GLM_RUNID = "atmosa"
GLM_START_DAY = 0


def parse_args(args=None):
    """Argument parser."""
    ap = argparse.ArgumentParser(
        SCRIPT,
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog=f"""Usage:
./{SCRIPT} -p trap1e -l trap1e -i ~/path/to/inp/dir/ -o ~/path/to/out/dir
""",
    )

    ap.add_argument("-i", "--inpdir", type=str, help="Input directory")
    ap.add_argument("-o", "--outdir", type=str, help="Output directory")
    # ap.add_argument(
    #     "-r",
    #     "--rose",
    #     action="store_true",
    #     default=False,
    #     help="Read data from a rose suite",
    # )
    ap.add_argument(
        "-l", "--label", type=str, required=True, help="Simulation label"
    )
    ap.add_argument(
        "-p", "--planet", type=str, required=True, help="Planet configuration"
    )
    ap.add_argument(
        "-s",
        "--startday",
        type=int,
        default=GLM_START_DAY,
        help="Load files with timestamp >= this",
    )
    ap.add_argument(
        "-e",
        "--endday",
        type=int,
        default=-1,
        help="Load files with timestamp <= this",
    )
    ap.add_argument(
        "--timestep",
        type=int,
        default=GLM_MODEL_TIMESTEP,
        help="Time step in seconds (for converting increments to SI units)",
    )
    ap.add_argument(
        "--letter",
        type=str,
        default="a,b,c,d,e,f,g",
        help="Letter(s) to identify files.",
    )
    ap.add_argument(
        "--ref_cube",
        type=str,
        default=um.sh,
        help="Reference cube, to which coordinates all data will be regridded",
    )
    ap.add_argument(
        "--no_extract_incr",
        action="store_true",
        default=False,
        help="Do NOT extract increment fields",
    )
    ap.add_argument(
        "--extract_inst",
        action="store_true",
        default=False,
        help="Extract instantaneous fields (if exist), otherwise extract mean",
    )
    ap.add_argument(
        "--no_regrid_multi_lev",
        action="store_true",
        default=False,
        help="Do NOT regrid multi-level variables to a common grid",
    )
    ap.add_argument(
        "--no_roll_cube_pm180",
        action="store_true",
        default=False,
        help="Do NOT roll cubes to +/- 180 degrees in longitude",
    )
    ap.add_argument(
        "--add_calendar",
        action="store_true",
        default=False,
        help="Add planet-specific calendar, if available",
    )
    ap.add_argument(
        "--use_varpack",
        action="store_true",
        default=False,
        help="Include only the variables from the `varpack`",
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

    # Input directory
    # inpdir = mypaths.sadir / label
    inpdir = Path(args.inpdir)
    L.info(f"{inpdir=}")

    # Create a subdirectory for processed data
    outdir = Path(args.outdir)
    # outdir = mypaths.sadir / label / "_processed"
    outdir.mkdir(parents=True, exist_ok=True)

    # Make a list of files matching the file mask and the start day threshold
    regex = GLM_RUNID + r".p" + r"[{}]".format(args.letter) + DEFAULT_REGEX
    L.info(regex)
    fnames = get_filename_list(
        inpdir,
        ts_start=args.startday,
        ts_end=args.endday,
        every=1,
        regex=regex,
        glob_pattern=f"{GLM_RUNID}*",
    )
    if len(fnames) == 0:
        L.critical("No files found!")
        return
    L.info(f"fnames({len(fnames)}) = {fnames[0]} ... {fnames[-1]}")

    cl_raw = load_data(fnames)
    if len(cl_raw) == 0:
        L.critical("Files are empty!")
        return

    # L.info(f"{cl_raw=}")

    timestep = args.timestep

    # Regrid & interpolate data
    cl_proc = process_cubes(
        cl_raw,
        timestep=timestep,
        ref_cube_constr=args.ref_cube,
        extract_incr=(not args.no_extract_incr),
        extract_mean=(not args.extract_inst),
        regrid_multi_lev=(not args.no_regrid_multi_lev),
        roll_pm180=(not args.no_roll_cube_pm180),
        add_calendar=args.add_calendar,
        planet=planet,
        use_varpack=args.use_varpack,
    )
    const = init_const(planet, directory=paths.const)
    add_planet_conf_to_cubes(cl_proc, const=const)

    if args.extract_inst:
        time_prof = "inst"
    else:
        time_prof = "mean"
    # Write the data to a netCDF file
    gl_attrs = {
        "name": label,
        "planet": planet,
        "timestep": timestep,
        "processed": "True",
    }
    days = args.startday + get_cube_rel_days(cl_proc[0]).astype(int)
    day_str = f"days{days[0]}"
    if len(days) > 1:
        day_str += f"_{days[-1]}"
    fname_out = outdir / f"{label}_{time_prof}_{day_str}.nc"
    save_cubelist(cl_proc, fname_out, **gl_attrs)
    L.success(f"Saved to {fname_out}")
    L.info(f"Execution time: {time() - t0:.1f}s")


if __name__ == "__main__":
    main()
