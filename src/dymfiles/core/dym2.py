"""
TODO : Describe
"""

import logging
import os

import numpy as np

from dymfiles.core import dym


class DymFileHeader(dym.DymFileHeader):
    """
    TODO : Describe
    """

    def __init__(self, filename):
        """
        Initializes the DymFileHeader class.

        Parameters:
        -----------
        filename : str
            Name of the DYM file.

        Returns:
        --------
        None
        """
        super().__init__(filename, "DYM2")

        self.idFunction_ = np.int32(0)
        self.minVal_ = np.float32(0)
        self.maxVal_ = np.float32(0)
        self.firstDate_ = np.float32(0)
        self.lastDate_ = np.float32(0)
        self.xLon_ = []
        self.yLat_ = []
        self.zLev_ = []
        self.mask_ = []

    def header_size(self) -> int:
        """Calculates the size of the Dym file header in bytes."""
        return (
            4 * self.sizeofChar_
            + 4 * self.sizeofInt_
            + 4 * self.sizeofFloat_
            + 2 * self.nLon_ * self.nLat_ * self.sizeofFloat_
            + 1 * self.nLon_ * self.nLat_ * self.sizeofInt_
            + self.nLev_ * self.sizeofFloat_
        )

    def read_header(self) -> None:
        """
        Reads header information from a binary file and sets instance variables.

        Returns
        -------
        None.

        Raises
        ------
        RuntimeError
            If an error occurs while reading the header.

        Notes
        -----
        This function expects a binary file containing header information and data to be
        located at the file path specified by the `fileName_` attribute of the class.

        The binary file must contain the following information in order:

        - A 4-byte string specifying the file format.
        - An integer specifying the function ID.
        - Two floating point values representing the minimum and maximum values.
        - Three integers representing the number of longitude points, latitude points, and
        vertical levels, respectively.
        - Two floating point values representing the first and last dates.
        - Data for the longitude, latitude, vertical level, and mask variables, each
        represented as an array of floating point or integer values.
        """

        def _extract_headers_values(self, fo):
            self.idFormat_ = fo.read(4).decode("utf-8")
            self.idFunction_ = np.fromfile(fo, "i", 1, "")[0]
            self.minVal_ = np.fromfile(fo, "f", 1, "")[0]
            self.maxVal_ = np.fromfile(fo, "f", 1, "")[0]
            self.nLon_ = np.fromfile(fo, "i", 1, "")[0]
            self.nLat_ = np.fromfile(fo, "i", 1, "")[0]
            self.nLev_ = np.fromfile(fo, "i", 1, "")[0]
            self.firstDate_ = np.fromfile(fo, "f", 1, "")[0]
            self.lastDate_ = np.fromfile(fo, "f", 1, "")[0]
            blocsize = self.nLon_ * self.nLat_
            data = np.fromfile(fo, "f", blocsize, "")
            data.resize(self.nLat_, self.nLon_)
            self.xLon_ = np.transpose(data)
            data = np.fromfile(fo, "f", blocsize, "")
            data.resize(self.nLat_, self.nLon_)
            self.yLat_ = np.transpose(data)
            self.zLev_ = np.fromfile(fo, "f", self.nLev_, "")
            data = np.fromfile(fo, "i", blocsize, "")
            data.resize(self.nLat_, self.nLon_)
            self.mask_ = np.transpose(data)

        try:
            with open(self.fileName_, "rb") as fo:
                _extract_headers_values(self, fo)
        except IOError as e:
            logging.error(
                f"read_header fails to read {e.fileName_}", exc_info=True
            )
            raise RuntimeError
        except Exception as e:
            logging.error(f"Header fails. Exception {e}", exc_info=True)
            raise RuntimeError
        finally:
            fo.close()


class DymFile(dym.DymFile):
    """Class representing a DYM2 data file."""

    def __init__(self, filename):
        """
        Initializes the DymFile class.

        Parameters:
        -----------
        filename : str
            The name of the DYM2 data file.
        """
        super().__init__(filename, "DYM2")
        self.dataFile_ = self.fileName_
        self.header_ = DymFileHeader(self.dataFile_)
        if os.path.isfile(self.dataFile_):
            self.read_header()

    def read_header(self) -> None:
        """Reads the DYM2 file header."""
        self.header_.read_header()

    def header_size(self) -> int:
        """Computes the size of the DYM2 file header."""
        return self.header_.header_size()
