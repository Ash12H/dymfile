"""TODO : Describe."""

import logging
import os
import sys
import xml.etree.ElementTree as ET
import zipfile

import numpy as np


def get_file_format(filename: str) -> str:
    """
    Get DYM file format.

    Parameters
    ----------
    filename : str
        file name

    Returns
    -------
    str
        file format in ["DYM2","DYM3","DYMZ","UNKNOWN"]
    """
    unknown = "UNKNOWN"
    with open(filename, "rb") as fo:
        IdFormat = fo.read(4).decode("utf-8")
    if IdFormat in ["DYM2", "DYM3"]:
        return IdFormat

    try:
        # Try to unzip file
        zfile = zipfile.ZipFile(filename)
    except Exception as e:
        logging.warning(f"{filename} : not a dym[2,3,Z] file. Exception : {e}")
        return unknown

    list_of_files = zfile.namelist()
    if len(list_of_files) != 2:
        logging.warning(
            f"{filename}: expecting 2 files in archive, {len(list_of_files)} found."
        )
        return unknown

    try:
        meta = next(a for a in list_of_files if a[-3:] == "xml")
    except Exception as e:
        logging.warning(
            f"{filename}: no meta file found in zip archive. exception : {e}"
        )
        return unknown

    try:
        data = next(a for a in list_of_files if ".dym" in a)
    except Exception as e:
        logging.warning(
            f"{filename}: no data file found in zip archive. Exception : {e}"
        )
        return unknown

    fo = zfile.open(data, "r")
    IdFormat = fo.read(4).decode("utf-8")
    fo.close()
    if IdFormat != "DYM3":
        logging.warning(f"{filename}: data file in dymz archive: unknown format.")
        return unknown

    fo = zfile.open(meta, "r")

    try:
        ET.parse(fo)
        fo.close()
    except Exception as e:
        fo.close()
        logging.warning(sys.exc_info())
        logging.warning(
            f"{filename}: meta file in dymz archive: unknown format. Exception : {e}"
        )
        return unknown

    return "DYMZ"


class DymFileHeader:
    """
    Header d'un fichier DYM.

    Attributes
    ----------
    fileName_ : str
        Nom du fichier.
    idFormat_ : int
        Format de l'identifiant.
    nLon_ : numpy.int32
        Nombre de points en longitude.
    nLat_ : numpy.int32
        Nombre de points en latitude.
    nLev_ : numpy.int32
        Nombre de niveaux.

    Methods
    -------
    header_size() -> int
        Calcule la taille de l'en-tête du fichier.
    data_block_size() -> int
        Calcule la taille en octets d'un bloc de données.
    dataSize() -> int
        Calcule la taille en octets de toutes les données.
    fileSize() -> int
        Calcule la taille totale du fichier.
    """

    def __init__(self, filename: str, idformat: int) -> None:
        """
        Initialise une instance de la classe DymFileHeader.

        Parameters
        ----------
        filename : str
            Nom du fichier.
        idformat : int
            Format de l'identifiant.
        """
        self.sizeofChar_ = 1
        self.sizeofInt_ = 4
        self.sizeofFloat_ = 4

        self.fileName_ = filename
        self.idFormat_ = idformat
        self.nLon_ = np.int32(0)
        self.nLat_ = np.int32(0)
        self.nLev_ = np.int32(0)

    def header_size(self) -> int:
        """Calcule la taille de l'en-tête du fichier."""
        return 0

    def data_block_size(self) -> int:
        """Calcule la taille en octets d'un bloc de données."""
        return self.nLon_ * self.nLat_ * self.sizeofFloat_


class DymFile:
    """
    A class for reading DYM files.

    Parameters
    ----------
    filename : str
        DYM file name.
    dymformat : str, optional
        DYM file format (to be set for creating new file).

    Attributes
    ----------
    fileName_ : str
        DYM file name.
    format_ : str
        DYM file format.
    dataFile_ : str or None
        The data file.
    header_ : DymFileHeader
        The header of the DYM file.

    Methods
    -------
    header_size()
        Return the header size of the DYM file.

    data_block_size()
        Return the data block size of the DYM file.

    dataSize()
        Return the data size of the DYM file.

    fileSize()
        Return the file size of the DYM file.

    read_header()
        Read the header of the data file.

    read_data(level=1)
        Read one data matrix.

    readAllData()
        Read all data matrix of the DYM file.

    """

    def __init__(self, filename, dymformat=None) -> None:
        """
        Initialize a DYM file reader.

        Parameters
        ----------
        filename : str
            DYM file name.
        dymformat : str, optional
            DYM file format (to be set for creating new file).

        Raises
        ------
        RuntimeError
            If no file format is selected and the file does not exist, or if the
            dymformat is not consistent with the file format.

        """
        self.fileName_ = filename

        if os.path.exists(filename):
            idformat = get_file_format(filename)
            if dymformat is not None and dymformat != idformat:
                msg = f"{self.fileName_}: dymformat is not consistent with file format. Expected format: {dymformat}. Found format: {idformat}."
                raise RuntimeError(msg)
            self.format_ = idformat

        elif dymformat is None:
            msg = "No file format selected."
            raise RuntimeError(msg)
        else:
            self.format_ = dymformat
        self.dataFile_ = None
        self.header_ = DymFileHeader(self.dataFile_, self.format_)

    def header_size(self) -> int:
        """Return the header size of the DYM file."""
        return self.header_.header_size()

    def data_block_size(self) -> int:
        """Return the data block size of the DYM file."""
        return self.header_.data_block_size()

    def read_header(self) -> None:
        """Read the header of the data file."""
        self.header_.read_header()

    def read_data(self, level: int = 1) -> np.ndarray:
        """
        Read one data matrix.

        Parameters
        ----------
        level : int, optional
            The level to read. Default is 1.

        Returns
        -------
        numpy.ndarray
            The data matrix.

        Raises
        ------
        IOError
            If the data file does not exist.
        """
        if not os.path.exists(self.dataFile_):
            msg = f"{self.dataFile_}: no such file."
            raise OSError(msg)

        blocsize = self.data_block_size()

        skip = np.int64(self.header_size()) + np.int64(blocsize) * (level - 1)

        with open(self.dataFile_, "rb") as fo:
            fo.seek(skip)
            data = np.fromfile(fo, "f", blocsize, "")
            data.resize(self.header_.nLat_, self.header_.nLon_)

        return data
