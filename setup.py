from setuptools import setup

if __name__ == "__main__":
    setup(
        name="dymfile",
        author="Jules Lehodey",
        version="0.1",
        packages=["dymfile"],
        package_dir={"dymfile": "src/dymfile"},
        scripts=["src/dymfile/scripts/dymtonetcdf.py"],
    )
