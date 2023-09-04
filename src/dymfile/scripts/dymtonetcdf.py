#!/usr/bin/env python
"""
A script which convert a DYM file into a NetCDF.

Usage: dymtonetcdf.py -i ./my_dym_file.dym -v my_variable_name -./new_netcdf_file.nc -a
    unit="meter" origin="country_X"
"""

import argparse
import logging
import time

from dymfile.dym2todataarray import dym2_to_data_array


def set_verbose(verbose: bool) -> None:
    """
    Set the script verbosity.

    Parameters
    ----------
    verbose : bool
        Whether or not to set the verbosity.
    """
    if verbose:
        fmt = "%(asctime)s - %(filename)s - %(levelname)s - %(message)s"
        logging.basicConfig(format=fmt, level=logging.DEBUG, datefmt="%Y-%m-%d %H:%M:%S")
        logging.Formatter.converter = time.gmtime


def usage() -> argparse.Namespace:
    """
    Program syntax
    """

    descr = "Convert a Dymfile into a netcdf file "
    fc = argparse.ArgumentDefaultsHelpFormatter
    parser = argparse.ArgumentParser(
        prog=__file__, description=descr, formatter_class=fc
    )

    parser.add_argument("--silent", "-s", help="Silent mode", action="store_true")
    parser.add_argument(
        "--infilepath",
        "-i",
        help="The path to the dymfile to convert",
        required=True,
    )
    parser.add_argument("--varname", "-v", help="The variable name", required=True)
    parser.add_argument(
        "--outfilepath",
        "-o",
        help="The path to the generated netcdf file",
        default="./output.nc",
    )
    parser.add_argument(
        "--attributs",
        "-a",
        nargs="*",
        help=(
            "List of attributs you want to add to the netdcf file. Format is : "
            'attribut_name="attribut content"'
        ),
        required=False,
    )

    return parser.parse_args()


def main() -> None:
    """Main function used by the script. Check argument then execute
    `dym2_to_data_array` function and save created file."""
    args = usage()

    set_verbose(not args.silent)

    infilepath = args.infilepath
    varname = args.varname
    outfilepath = args.outfilepath
    attributs = None
    if args.attributs is not None:
        attributs = dict(data.split("=", maxsplit=1) for data in args.attributs)

    dataarray = dym2_to_data_array(
        infilepath=infilepath, varname=varname, attributs=attributs
    )

    dataarray.to_netcdf(outfilepath)


if __name__ == "__main__":
    main()
