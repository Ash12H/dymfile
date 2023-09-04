from __future__ import annotations
import numpy as np
from dataclasses import dataclass
import datetime
import itertools
import io
import xarray as xr
import struct


def _get_date_sea(ndat):
    year = int(ndat)
    days = int((ndat - year) * 365)
    date = datetime.date(year, 1, 1) + datetime.timedelta(days=days - 1)
    return date


def _year_month_sea(ndat):
    year = int(ndat)
    days = int((ndat - year) * 365)
    date = datetime.date(year, 1, 1) + datetime.timedelta(days=days - 1)
    month = date.month
    return [year, month]


def _gen_monthly_dates(t0, tfin):
    dates = [
        datetime.date(year, month, 15)
        for year, month in itertools.product(
            range(t0[0], tfin[0] + 1), range(t0[1], tfin[1] + 1)
        )
    ]
    return np.array(dates, dtype="datetime64")


def _iter_unpack_numbers(
    format: str, buffer: io.BufferedReader | io.BytesIO
) -> np.ndarray:
    result = struct.iter_unpack(format, buffer)
    return np.array([x[0] for x in result])


@dataclass
class HeaderData:
    nlon: int
    nlat: int
    nlevel: int
    t0_file: float
    tfin_file: float


def read_header(
    file: io.BufferedReader | io.BytesIO,
) -> tuple[HeaderData, np.ndarray, np.ndarray]:
    """Read informations in the Dymfile header."""
    file.read(4)
    struct.unpack("i", file.read(4))
    struct.unpack("f", file.read(4))
    struct.unpack("f", file.read(4))

    nlon = struct.unpack("i", file.read(4))[0]
    nlat = struct.unpack("i", file.read(4))[0]
    nlevel = struct.unpack("i", file.read(4))[0]
    t0_file = struct.unpack("f", file.read(4))[0]
    tfin_file = struct.unpack("f", file.read(4))[0]

    header_data = HeaderData(nlon, nlat, nlevel, t0_file, tfin_file)
    xlon = np.zeros((header_data.nlat, header_data.nlon), dtype=np.float32)
    ylat = np.zeros((header_data.nlat, header_data.nlon), dtype=np.float32)

    return header_data, xlon, ylat


def init_data(
    file: io.BufferedReader | io.BytesIO,
    header_data: HeaderData,
    xlon: np.ndarray,
    ylat: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Initialize coordinates and mask."""
    for i in range(header_data.nlat):
        xlon[i, :] = _iter_unpack_numbers("f", file.read(4 * header_data.nlon))
    for i in range(header_data.nlat):
        ylat[i, :] = _iter_unpack_numbers("f", file.read(4 * header_data.nlon))
    time_vect = _iter_unpack_numbers("f", file.read(4 * header_data.nlevel))
    mask = np.zeros((header_data.nlat, header_data.nlon), dtype=np.int32)
    for i in range(header_data.nlat):
        mask[i, :] = _iter_unpack_numbers("i", file.read(4 * header_data.nlon))
    return xlon, ylat, time_vect, mask


def fill_data(
    file: io.BufferedReader | io.BytesIO,
    header_data: HeaderData,
) -> np.ndarray:
    """Fill the data array."""
    data = np.zeros(
        (header_data.nlevel, header_data.nlat, header_data.nlon),
        dtype=np.float32,
    )
    iterator = itertools.product(range(header_data.nlevel), range(header_data.nlat))
    for time, lat in iterator:
        result = struct.iter_unpack("f", file.read(4 * header_data.nlon))
        data[time, lat, :] = np.array([x[0] for x in result])
    # Convert invalid values in DYM to NA
    data[data == -999] = np.nan
    return data


def format_date(delta_time: int, header_data: HeaderData) -> np.ndarray:
    """Transform the date (float) into datetime format."""
    if delta_time == 30:
        dates = _gen_monthly_dates(
            _year_month_sea(header_data.t0_file),
            _year_month_sea(header_data.tfin_file),
        )
    else:
        dates = _get_date_sea(header_data.t0_file) + np.arange(
            0, header_data.nlevel * delta_time, delta_time
        )
    return np.array(dates, dtype="datetime64")


def loading(
    file: io.BufferedReader | io.BytesIO,
    *,
    date_formating: bool = True,
    delta_time: int = 30,
):
    """Wrapper function. Load all the data into numpy format."""
    header_data, xlon, ylat = read_header(file)
    xlon, ylat, time_vector, mask = init_data(file, header_data, xlon, ylat)
    if date_formating:
        time_vector = format_date(delta_time, header_data)
    data = fill_data(file, header_data)

    return data, mask, time_vector, xlon, ylat


def format_data(data, mask, time_vector, xlon, ylat):
    """Transform the numpy data into Xarray format."""
    ylat = ylat[:, 0]
    xlon = xlon[0, :]

    mask = xr.DataArray(
        mask,
        dims=("lat", "lon"),
        coords={"lat": ylat, "lon": xlon},
        name="mask",
    )
    data = xr.DataArray(
        data,
        dims=("time", "lat", "lon"),
        coords={
            "time": time_vector,
            "lat": ylat,
            "lon": xlon,
        },
    )
    data = xr.where(mask == 0, np.NAN, data)
    data = data.transpose("time", "lat", "lon")
    data = data.sortby(["time", "lat", "lon"])
    mask = mask.sortby(["lat", "lon"])

    return data, mask
