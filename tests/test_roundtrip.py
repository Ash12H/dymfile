"""Tests for DYM write and round-trip operations."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import xarray as xr

from dymfile.reader import dym_to_dataset, read_dym
from dymfile.writer import DYM_FORMAT_ID, dataset_to_dym, write_dym


def _grid() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """A small field on a grid given from south to north, with land and a gap."""
    rng = np.random.default_rng(0)
    longitude = np.array([120.0, 122.0, 124.0, 126.0])
    latitude = np.array([-2.0, 0.0, 2.0])
    time = 2020.0 + (np.arange(3) + 0.5) / 12.0
    data = rng.uniform(15.0, 30.0, (3, 3, 4))
    mask = np.array([[1, 1, 0, 3], [2, 3, 3, 0], [3, 3, 3, 3]], dtype=np.int32)
    data[1, 2, 1] = np.nan
    return data, longitude, latitude, time, mask


def test_roundtrip_basic(sample_dym_file: Path, tmp_dym_file: Path) -> None:
    """Test read -> write -> read round-trip."""
    # Read original
    original_data = read_dym(sample_dym_file)

    # Write to temporary file
    write_dym(
        tmp_dym_file,
        data=original_data.data,
        longitude=original_data.longitude,
        latitude=original_data.latitude,
        time=np.arange(
            original_data.header.t0,
            original_data.header.tfin,
            (original_data.header.tfin - original_data.header.t0)
            / original_data.header.nlevel,
        ).astype(np.float32),
        mask=original_data.mask,
        t0=original_data.header.t0,
        tfin=original_data.header.tfin,
    )

    # Read back
    reread_data = read_dym(tmp_dym_file)

    # Compare headers
    assert reread_data.header.nlon == original_data.header.nlon
    assert reread_data.header.nlat == original_data.header.nlat
    assert reread_data.header.nlevel == original_data.header.nlevel

    # Compare arrays
    np.testing.assert_array_equal(reread_data.mask, original_data.mask)
    np.testing.assert_allclose(reread_data.longitude, original_data.longitude)
    np.testing.assert_allclose(reread_data.latitude, original_data.latitude)

    # Compare data (allowing for NaN)
    np.testing.assert_allclose(
        reread_data.data, original_data.data, equal_nan=True, rtol=1e-5
    )


def test_roundtrip_dataset(sample_dym_file: Path, tmp_dym_file: Path) -> None:
    """Test Dataset round-trip using high-level API."""
    # Read as dataset
    original_ds = dym_to_dataset(sample_dym_file, decode_times=False)

    # Write back
    dataset_to_dym(original_ds, tmp_dym_file)

    # Read back
    reread_ds = dym_to_dataset(tmp_dym_file, decode_times=False)

    # Compare dimensions
    assert reread_ds.dims == original_ds.dims

    # Get first data variable (excluding mask)
    data_vars = [v for v in original_ds.data_vars if v != "mask"]
    if data_vars:
        var_name = data_vars[0]
        np.testing.assert_allclose(
            reread_ds[var_name].values,
            original_ds[var_name].values,
            equal_nan=True,
            rtol=1e-5,
        )


def test_header_carries_the_format_identifier(tmp_dym_file: Path) -> None:
    """The file starts with DYM2, then a function identifier, then the data's range."""
    data, longitude, latitude, time, mask = _grid()
    write_dym(tmp_dym_file, data, longitude, latitude, time, mask)

    raw = tmp_dym_file.read_bytes()
    assert raw[:4] == DYM_FORMAT_ID
    minval, maxval = np.frombuffer(raw, "<f4", 2, 8)
    valid = data[:, mask > 0]
    assert minval == np.float32(np.nanmin(valid))
    assert maxval == np.float32(np.nanmax(valid))


def test_rows_are_written_from_north_to_south(tmp_dym_file: Path) -> None:
    """A grid given from south to north is written reversed, data and mask with it."""
    data, longitude, latitude, time, mask = _grid()
    write_dym(tmp_dym_file, data, longitude, latitude, time, mask)

    reread = read_dym(tmp_dym_file)
    np.testing.assert_array_equal(reread.latitude, latitude[::-1])
    np.testing.assert_array_equal(reread.mask, mask[::-1, :])
    sea = mask[::-1, :] > 0
    np.testing.assert_allclose(
        reread.data[:, sea], data[:, ::-1, :][:, sea], rtol=1e-6, equal_nan=True
    )


def test_dataset_roundtrip_in_any_dimension_order(tmp_dym_file: Path) -> None:
    """A dataset reads back the same, whatever the order of its dimensions."""
    data, longitude, latitude, time, mask = _grid()
    field = xr.DataArray(
        data,
        dims=("time", "latitude", "longitude"),
        coords={"time": time, "latitude": latitude, "longitude": longitude},
    ).where(mask > 0)
    ds = xr.Dataset(
        {
            "temperature": field.transpose("latitude", "longitude", "time"),
            "mask": xr.DataArray(mask, dims=("latitude", "longitude")).T,
        }
    )
    dataset_to_dym(ds, tmp_dym_file, variable="temperature")

    reread = dym_to_dataset(tmp_dym_file, decode_times=False)
    order = ("time", "latitude", "longitude")
    np.testing.assert_allclose(
        reread[tmp_dym_file.stem].transpose(*order).values,
        field.transpose(*order).values,
        rtol=1e-6,
        equal_nan=True,
    )
    np.testing.assert_array_equal(reread["mask"].values, mask)
