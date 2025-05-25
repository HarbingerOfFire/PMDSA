# Class for the FITS file format
# Flexible Image Transport System (FITS) is an open standard defining a digital file format 
# useful for storage, transmission and processing of data: formatted as multi-dimensional 
# arrays (for example a 2D image), or tables. - Wikipedia (https://en.wikipedia.org/wiki/FITS)

# LINK FOR FITS FORMAT (NASA):
# https://heasarc.gsfc.nasa.gov/docs/heasarc/fits_overview.html
# https://fits.gsfc.nasa.gov/standard40/fits_standard40aa-le.pdf

'''
Attributes:
    file (IO[bytes]): The file object of the FITS file
    header (header.Header): The header of the FITS file
    history (list[str]): The history entries from the header of the FITS file
    data (np.ndarray): The data of the FITS file as a numpy array (NAXIS1 x NAXIS2)
    wcs (wcs.WCS): The WCS object of the FITS file (See FITS/wcs.py)

Methods:
    ensure_header_value (bool): ensure value is in header before using
    _read_header (None): Reads the header of the FITS file and stores it in the header attribute
    _read_data (None): Reads the data of the FITS file and stores it in the data attribute
    _binary_to_array (np.ndarray): Converts the binary data of the FITS file into a numpy array
    __del__ (None): Ensures the file is properly closed when the object is deleted
'''

from typing import IO
from math import ceil
from . import header, wcs
import numpy as np

class FITS:
    def __init__(self, file: IO[bytes]):
        self.file: IO[bytes] = file
        self.filename = self.file.name
        self.header: header.Header = header.Header()
        self.history: list[str] = []
        self.data: np.ndarray = None
        self.wcs: wcs.WCS = None
        self._read_header()
        self._read_data()

    def ensure_header_value(self, value:str)-> bool:
        """
        Ensure value is in header before using

        Parameters:
            value (str): The key for header inquiry
        
        Returns:
            bool: the truth of the key's existance
        """
        try:
            self.header[value]
            return True
        except KeyError:
            return False

    
    def _binary_to_array(self, binary_data: bytes, bpix: int, NAXIS1: int, NAXIS2: int):
        """
        Convert a binary string into a NAXIS2 x NAXIS1 array of integers.
        
        Parameters:
            binary_data (bytes): The binary string.
            bpix (int): Bytes per pixel.
            NAXIS1 (int): Width of the image.
            NAXIS2 (int): Height of the image.
        
        Returns:
            np.ndarray: The reshaped array.
        """
      
        # Convert binary data to numpy array
        array = np.frombuffer(binary_data, dtype=f">u{bpix}")
        
        # Reshape into 2D array
        return array.reshape((NAXIS2, NAXIS1))

    def _read_header(self):
        '''This function parses the header of a FITS file and returns a dictionary of the header data and a list of the history data'''
        END=False
        while not END:
            # FITS files store header data in 80-byte blocks
            line = self.file.read(80).decode("utf-8")
            # the last block is END followed by 77 spaces
            if "END" == line.strip():
                END=True
                continue
            try:
                line=line.split("/")[0] # remove comments
                key, value = line.split("=")
                self.header[key.strip()]=value.strip()
            except ValueError:
                # value error when there is not enough data to unpack for a key value pair
                if "HISTORY" in line:
                    self.history.append(line)
                pass
        assert self.header["SIMPLE"] == "T", "Not a FITS file"
        assert int(self.header["BITPIX"]) in [8, 16, 32, 64], "Unsupported BITPIX value"
        assert int(self.header["NAXIS"]) == 2, "Only 2D images supported"
        assert int(self.header["NAXIS1"]) > 0 and int(self.header["NAXIS2"]) > 0, "Invalid image dimensions"
        self.wcs=wcs.WCS(self.header)
        return self.header
    
    def _read_data(self):
        #skip block size (2880 bytes)
        place=self.file.tell()
        blockEnd=ceil(place/2880)*2880
        self.file.seek(blockEnd)

        #####RETRIEVE DATA AND CONVERT TO ARRAY#####
        bytepix=int(self.header["BITPIX"])//8
        width=int(self.header["NAXIS1"])
        height=int(self.header["NAXIS2"])

        self.data=self.file.read(bytepix*width*height)
        self.data=self._binary_to_array(self.data, int(self.header["BITPIX"])//8, int(self.header["NAXIS1"]), int(self.header["NAXIS2"]))
        if self.ensure_header_value("BSCALE") and self.ensure_header_value("BZERO"):
            self.data = (self.data * int(self.header["BSCALE"]))+int(self.header["BZERO"])
        return self.data
        
    def __del__(self):
        '''Properly close file on delete'''
        self.file.close()


###################################
# EXAMPLE FOR READING A FITS FILE #
###################################
if __name__=="__main__":
    from pprint import pprint
    with open("/run/user/1000/gvfs/smb-share:server=nas.local,share=secureshare/DATA/08554+7048_V/08554+7048-V-20250218-002-021746_out.fits", "rb") as f:
        fits = FITS(f)
        fits.wcs.sky_scale()
        pprint(fits.header)
        pprint(fits.wcs)
        print(tuple((fits.data.dtype, fits.data.shape)))