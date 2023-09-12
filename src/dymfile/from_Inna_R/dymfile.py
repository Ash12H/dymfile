"""Main class used to manage DYM files."""

from __future__ import annotations

import io
from functools import singledispatchmethod
from pathlib import Path
from typing import TYPE_CHECKING, Any

import hvplot.xarray  # noqa: F401
import xarray as xr

from dymfile.from_Inna_R import dymfile_loading, dymfile_tools

if TYPE_CHECKING:
    import cartopy.crs as ccrs


class Dymfile:
    """
    Represents a Dymfile object.

    This class provides methods for initializing a Dymfile object, loading data from
    different sources, and plotting the data and mask.

    Attributes
    ----------
    data : xr.DataArray
        An xarray DataArray representing the data.
    mask : xr.DataArray
        An xarray DataArray representing the mask.

    Methods
    -------
    __init__:
        Initializes a Dymfile object. Use Xarray.DataArray objects for data and mask.
    from_input:
        Load a Dymfile from an input source. Use either a filepath or a buffer wich
        correspond to a Dymfile.
    plot_data:
        Plots the data contained in the Dymfile as a quadmesh plot.
    plot_mask:
        Plots the mask contained in the Dymfile.

    Parameters
    ----------
    data : xr.DataArray
        An xarray DataArray representing the data.
    mask : xr.DataArray
        An xarray DataArray representing the mask.
    normalize_longitude : bool, optional
        Whether to normalize the longitude. Defaults to False.

    Examples
    --------
    >>> import xarray as xr
    >>> from dymfile import Dymfile

    >>> # Create data and mask xarray DataArrays
    >>> data = xr.DataArray(...)
    >>> mask = xr.DataArray(...)

    >>> # Create a Dymfile object
    >>> dymfile = Dymfile(data, mask, normalize_longitude=True)

    >>> # Load a Dymfile from a filepath
    >>> filepath = "/path/to/dymfile.nc"
    >>> dymfile_from_file = Dymfile.from_input(filepath, normalize_longitude=True)
    """

    def __init__(
        self: Dymfile,
        data: xr.DataArray,
        mask: xr.DataArray,
        *,
        normalize_longitude: bool = False,
    ) -> None:
        """
        Initializes a Dymfile object.

        Parameters
        ----------
        data : xr.DataArray
            An xarray DataArray representing the data.
        mask : xr.DataArray
            An xarray DataArray representing the mask.
        normalize_longitude : bool, optional
            Whether to normalize the longitude. Defaults to False.

        Notes
        -----
        If `normalize_longitude` is True, the longitude is normalized using the
        `dymfile_tools.normalize_longitude()` function.
        """
        with xr.set_options(keep_attrs=True):
            if normalize_longitude:
                data = dymfile_tools.normalize_longitude(data)
            dymfile_tools.normalize_longitude(data)
            self.data = data
            self.mask = mask

    @singledispatchmethod
    @classmethod
    def from_input(
        cls: Dymfile,
        input_source: bytes | str,  # noqa: ARG003
        delta_time: int = 30,  # noqa: ARG003
        *,
        name: str | None = None,  # noqa: ARG003
        normalize_longitude: bool = False,  # noqa: ARG003
        date_formating: bool = True,  # noqa: ARG003
    ) -> Dymfile:
        """
        Load a Dymfile from an input source. Input can be a filepath or a buffer of
        bytes.

        Parameters
        ----------
        input_source : str | bytes
            The input source to load the Dymfile from.
        delta_time : int, optional
            The time delta, by default 30 (Monthly).
        date_formating : bool, optional
            Whether to format dates (to datetime), by default True.
        normalize_longitude : bool, optional
            Whether to normalize the longitude (between [-180, 180]), by default False.
        name : str | None, optional
            The name of the Dymfile, by default None.
        """
        error_message = "Unsupported input source"
        raise NotImplementedError(error_message)

    @from_input.register(str)
    @classmethod
    def _from_filepath(
        cls: Dymfile,
        filepath: str,
        delta_time: int = 30,
        *,
        name: str | None = None,
        units: str | None = None,
        normalize_longitude: bool = False,
        date_formating: bool = True,
    ) -> Dymfile:
        """
        Load a Dymfile from a filepath.

        This method is a classmethod that registers the `_from_filepath` implementation
        as a handler for loading a Dymfile from a filepath. It reads the data, mask,
        time vector, longitude, and latitude from the file using the
        `dymfile_loading.loading()` function. Then, it formats the data and mask using
        the `dymfile_loading.format_data()` function. Finally, it creates and returns a
        Dymfile object with the loaded data and mask.
        """
        file = Path(filepath)
        if name is None:
            name = file.stem
        with file.open("rb") as file:
            data, mask, time_vector, xlon, ylat = dymfile_loading.loading(
                file, delta_time=delta_time, date_formating=date_formating
            )
        data, mask = dymfile_loading.format_data(
            data, mask, time_vector, xlon, ylat, name, units
        )
        return Dymfile(data, mask, normalize_longitude=normalize_longitude)

    @from_input.register(bytes)
    @classmethod
    def _from_buffer(
        cls: Dymfile,
        buffer: bytes,
        delta_time: int = 30,
        *,
        name: str | None = None,
        units: str | None = None,
        normalize_longitude: bool = False,
        date_formating: bool = True,
    ) -> Dymfile:
        """
        Load a Dymfile from a buffer of bytes.

        This method is a classmethod that registers the `_from_buffer` implementation as
        a handler for loading a Dymfile from a buffer of bytes. It reads the data, mask,
        time vector, longitude, and latitude from the buffer using the
        `dymfile_loading.loading()` function. Then, it formats the data and mask using
        the `dymfile_loading.format_data()` function. Finally, it creates and returns a
        Dymfile object with the loaded data and mask.

        """
        if name is None:
            name = "Dymfile"
        with io.BytesIO(buffer) as buffer:
            data, mask, time_vector, xlon, ylat = dymfile_loading.loading(
                buffer, delta_time=delta_time, date_formating=date_formating
            )
        data, mask = dymfile_loading.format_data(
            data, mask, time_vector, xlon, ylat, name, units
        )
        return Dymfile(data, mask, normalize_longitude=normalize_longitude)

    def plot_data(self: Dymfile, projection: ccrs.Projection = None) -> Any:
        """Plots the data contained in the Dymfile as a quadmesh plot."""
        return dymfile_tools.plot(self.data, projection=projection)

    def plot_mask(self: Dymfile) -> Any:
        """Plots the mask contained in the Dymfile as a quadmesh plot."""
        return self.mask.plot()
