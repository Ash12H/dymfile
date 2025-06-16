#!/usr/bin/env python
"""
A script which convert a DYM file into a NetCDF.

Usage: dymtonetcdf.py -i ./my_dym_file.dym -v my_variable_name -./new_netcdf_file.nc -a
    unit="meter"
"""

import argparse

from dymfile import Dymfile


def usage() -> argparse.Namespace:
    """Program syntax."""
    descr = "Convert a Dymfile into a netcdf file "
    fc = argparse.ArgumentDefaultsHelpFormatter
    parser = argparse.ArgumentParser(
        prog=__file__, description=descr, formatter_class=fc
    )

    parser.add_argument("--silent", "-s", help="Silent mode", action="store_true")
    parser.add_argument(
        "--norm_lon",
        "-l",
        type=bool,
        default=True,
        help="Normalize the longitude coordinate between -180 and 180",
    )
    parser.add_argument(
        "--delta_time",
        "-t",
        type=int,
        default=30,
        help="Delta time between two time steps in days",
    )
    parser.add_argument(
        "--form_date",
        "-d",
        help="Format the date coordinate to datetime standard",
        type=bool,
        default=True,
    )
    parser.add_argument(
        "--infilepath",
        "-i",
        help="The path to the dymfile to convert",
        required=True,
    )
    parser.add_argument("--varname", "-v", help="The variable name", required=False)
    parser.add_argument(
        "--outfilepath",
        "-o",
        help="The path to the generated netcdf file",
        # TODO(Jules): may be removed if autocomputed  # noqa: TD003
        default="./output.nc",
    )

    return parser.parse_args()


def main() -> None:
    """
    Main function used by the script. Check argument then execute
    `dym2_to_data_array` function and save created file.
    """
    args = usage()

    infilepath = args.infilepath
    varname = args.varname
    outfilepath = args.outfilepath
    norm_lon = args.norm_lon
    form_date = args.form_date
    delta_time = args.delta_time

    dymfile: Dymfile = Dymfile.from_filepath(
        infilepath,
        normalize_longitude=norm_lon,
        date_formating=form_date,
        name=varname,
        delta_time=delta_time,
    )

    dymfile.data.to_netcdf(outfilepath)


if __name__ == "__main__":
    main()
