from __future__ import annotations
import xarray as xr
import io
from . import dymfile_tools
from pathlib import Path
import plotly.express as px


class Dymfile:
    def __init__(self: Dymfile, data: xr.DataArray, mask: xr.DataArray):
        self.data = data
        self.mask = mask

    @classmethod
    def from_file(
        cls: Dymfile,
        filepath: str | Path,
        *,
        date_formating: bool = True,
        delta_time: int = 30,
    ) -> Dymfile:
        with Path(filepath).open("rb") as file:
            data, mask, time_vector, xlon, ylat = dymfile_tools.loading(
                file, delta_time=delta_time, date_formating=date_formating
            )
        data, mask = dymfile_tools.format_data(data, mask, time_vector, xlon, ylat)
        return Dymfile(data, mask)

    @classmethod
    def from_buffer(
        cls: Dymfile,
        buffer: bytes,
        *,
        date_formating: bool = True,
        delta_time: int = 30,
    ) -> Dymfile:
        with io.BytesIO(buffer) as buffer:
            data, mask, time_vector, xlon, ylat = dymfile_tools.loading(
                buffer,
                delta_time=delta_time,
                date_formating=date_formating,
            )
        data, mask = dymfile_tools.format_data(data, mask, time_vector, xlon, ylat)
        return Dymfile(data, mask)

    def plot_data(self: Dymfile):
        return px.imshow(
            self.data,
            animation_frame="time",
            origin="lower",
            zmin=0,
            zmax=float(self.data.max()),
        )

    def plot_mask(self: Dymfile):
        return px.imshow(
            self.mask,
            origin="lower",
        )
