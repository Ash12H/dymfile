from setuptools import setup

if __name__ == "__main__":
    setup(
        name="dymfile",
        author="Jules Lehodey",
        version="0.1",
        package=["dymfile", "dymfile.core"],
        packages_dir={
            "dymfile": "src/dymfile",
            "dymfile.core": "src/dymfile/core",
        },
        scripts=["scripts/dymtonetcdf.py"],
        install_requires=[
            "numpy",
            "netCDF4",
            "xarray",
            "plotly",
            "ipykernel",
            "matplotlib",
            "cartopy",
            "hvplot",
            "geoviews",
            "jupyter_bokeh",
        ],
    )
