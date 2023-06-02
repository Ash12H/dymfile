"""
TODO : Describe
"""
import os
from typing import Any, Dict, Optional

import numpy as np
import xarray as xr

from dymfile.core import dym2, utilities


def dym2_to_data_array(
    infilepath: str, varname: str, attributs: Optional[Dict[str, Any]] = None
) -> xr.DataArray:
    """
    Generate an `xarray.DataArray` from a DYM file.

    Parameters
    ----------
    infilepath : str
        The path to the DYM file.
    varname : str
        The name of the generated DataArray.
    attributs : dict, optional
        Additional attributes to add to the generated DataArray, by default None.

    Returns
    -------
    xarray.DataArray
        The DataArray generated from the DYM file.

    Raises
    ------
    ValueError
        If the `infilepath` does not exist.

    Notes
    -----
    This function reads a DYM file using the `dym2` module and generates an
    `xarray.DataArray` from the data. The `xarray.DataArray` will have the
    dimensions 'time', 'lat', and 'lon', with the time dimension being
    inferred from the file's date information.

    Example usage:
        ```
        da = dym2_to_data_array('path/to/file.dym', 'my_data_array')
        ```
    """

    if not os.path.exists(infilepath):
        raise ValueError(f"File not found: {infilepath}")

    dym_file = dym2.DymFile(infilepath)

    longitude_vec = dym_file.header_.xLon_[:, 0]
    latitude_vec = dym_file.header_.yLat_[0, :]
    n_time = dym_file.header_.nLev_

    dict_time = dict(standard_name="time")
    dict_lat = dict(standard_name="latitude", units="degrees_north")
    dict_lon = dict(standard_name="longitude", units="degrees_east")

    grouped_outdata = []
    grouped_datestr = []

    # Extract all values from Dym structure and transform date
    for k in range(n_time):
        datestr = utilities.date_dym2tostr(dym_file.header_.zLev_[k])
        datestr = np.datetime64(f"{datestr[:4]}-{datestr[4:6]}-{datestr[6:8]}")
        grouped_datestr.append(datestr)
        filval = np.NaN
        outdata = dym_file.read_data(k + 1)
        outdata[outdata == 0] = filval
        grouped_outdata.append(outdata)

    return xr.DataArray(
        data=np.array(grouped_outdata),
        name=varname,
        dims=("time", "lat", "lon"),
        coords={
            "time": (
                "time",
                np.array(grouped_datestr, dtype="datetime64[D]"),
                dict_time,
            ),
            "lat": ("lat", latitude_vec, dict_lat),
            "lon": ("lon", longitude_vec, dict_lon),
        },
        attrs=attributs,
    )
