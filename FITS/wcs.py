################################
# CLASS FOR WCS OF A FITS FILE #
################################

# World Coordinate System (WCS) keywords in the header of a FITS or IRAF image file define 
# the relationship between pixel coordinates in the image and sky coordinates.
#                                              - Daniel Moser: https://github.com/danmoser

# LINK TO WCS FORMAT (GITHUB):
# https://danmoser.github.io/notes/gai_fits-imgs.html

#This class implements a basic linear WCS transform based on:
#  - Greisen & Calabretta (2002), A&A 395, 1061–1075
#  - Calabretta & Greisen (2002), A&A 395, 1077–1122
#and the IAU FITS Standard Version 4.0.

#References:
#  https://doi.org/10.1051/0004-6361:20021326
#  https://doi.org/10.1051/0004-6361:20021327
#  https://www.aanda.org/articles/aa/pdf/2002/45/aah3859.pdf
#  https://www.aanda.org/articles/aa/pdf/2002/45/aah3860.pdf
#  https://fits.gsfc.nasa.gov/fits_wcs.html

'''
ATTRIBUTES

WCS Transformation Matrix:
CD1_1 = CDELT1 * cos (CROTA2)
CD1_2 = -CDELT2 * sin (CROTA2)
CD2_1 = CDELT1 * sin (CROTA2)
CD2_2 = CDELT2 * cos (CROTA2)
WCS = [[CD1_1, CD1_2], 
       [CD2_1, CD2_2]]

CTYPE1
CTYPE2 indicate the coordinate type and projection.
- The first four characters are RA-- and DEC-, GLON and GLAT, or ELON and ELAT, for equatorial, galactic, and ecliptic coordinates, respectively.
- The second four characters contain a four-character code for the projection.

CRPIX1 and CRPIX2 are the pixel coordinates of the reference point to which the projection and the rotation refer.
CRVAL1 and CRVAL2 give the center coordinate as right ascension and declination or longitude and latitude in decimal degrees.

METHODS
SKY_ANGLE: Get the angle of the sky in degrees (atan2(CD2_1, CD1_1)) (Sets CROTA2)
SKY_SCALE: Get the scale of the sky in degrees per pixel (Sets CDELT1 and CDELT2)
'''

from dataclasses import dataclass, field
from math import atan2, degrees, cos, radians
import numpy as np

@dataclass
class WCS:
    header: dict
    CD1_1: float = field(init=False)
    CD1_2: float = field(init=False)
    CD2_1: float = field(init=False)
    CD2_2: float = field(init=False)
    WCS: list = field(init=False)
    CTYPE1: str = field(init=False)
    CTYPE2: str = field(init=False)
    CRPIX1: float = field(init=False)
    CRPIX2: float = field(init=False)
    CRVAL1: float = field(init=False)
    CRVAL2: float = field(init=False)
    CROTA2: float = field(init=False)
    CDELT1: float = field(init=False)
    CDELT2: float = field(init=False)

    def __post_init__(self):
        h = self.header
        self.CD1_1 = float(h['CD1_1'])
        self.CD1_2 = float(h['CD1_2'])
        self.CD2_1 = float(h['CD2_1'])
        self.CD2_2 = float(h['CD2_2'])

        self.WCS = [[self.CD1_1, self.CD1_2],
                    [self.CD2_1, self.CD2_2]]

        self.CTYPE1 = h['CTYPE1']
        self.CTYPE2 = h['CTYPE2']
        self.CRPIX1 = float(h['CRPIX1'])
        self.CRPIX2 = float(h['CRPIX2'])
        self.CRVAL1 = float(h['CRVAL1'])
        self.CRVAL2 = float(h['CRVAL2'])

        self.sky_angle()
        self.sky_scale()

    def __repr__(self):
        return (
            "{\n"
            f"  'CD1_1': {self.CD1_1!r},\n"
            f"  'CD1_2': {self.CD1_2!r},\n"
            f"  'CD2_1': {self.CD2_1!r},\n"
            f"  'CD2_2': {self.CD2_2!r},\n"
            f"  'WCS': {self.WCS!r},\n"
            f"  'CTYPE1': {self.CTYPE1!r},\n"
            f"  'CTYPE2': {self.CTYPE2!r},\n"
            f"  'CRPIX1': {self.CRPIX1!r},\n"
            f"  'CRPIX2': {self.CRPIX2!r},\n"
            f"  'CRVAL1': {self.CRVAL1!r},\n"
            f"  'CRVAL2': {self.CRVAL2!r},\n"
            f"  'CROTA2': {self.CROTA2!r},\n"
            f"  'CDELT1': {self.CDELT1!r},\n"
            f"  'CDELT2': {self.CDELT2!r}\n"
            "}"
        )

    def __str__(self):
        return f"{self.__class__.__name__}({self.WCS})"

    def sky_angle(self):
        self.CROTA2 = degrees(atan2(self.CD2_1, self.CD1_1))
        return self.CROTA2

    def sky_scale(self):
        if not hasattr(self, 'CROTA2'):
            self.sky_angle()
        self.CDELT1 = self.CD1_1 / cos(radians(self.CROTA2))
        self.CDELT2 = self.CD2_2 / cos(radians(self.CROTA2))
        return self.CDELT1, self.CDELT2

    def world_to_pixel(self, RA: float, Dec: float):
        delta_world = np.array([RA - self.CRVAL1, Dec - self.CRVAL2])
        CD_inv = np.linalg.inv(np.array(self.WCS))
        delta_pix = CD_inv @ delta_world
        pixel_coords = delta_pix + np.array([self.CRPIX1, self.CRPIX2])
        return pixel_coords[0], pixel_coords[1]

    def pixel_to_world(self, Pixel_x: float, Pixel_y: float):
        delta_pix = np.array([Pixel_x - self.CRPIX1, Pixel_y - self.CRPIX2])
        CD = np.array(self.WCS)
        delta_world = CD @ delta_pix
        RA_DEC = np.array([self.CRVAL1, self.CRVAL2]) + delta_world
        return RA_DEC[0], RA_DEC[1]


##################################
# EXAMPLE FOR WCS OF A FITS FILE #
##################################
from pprint import pprint
from random import random

if __name__=="__main__":
    # Example usage
    header = {
        'CD1_1': random(),
        'CD1_2': random(),
        'CD2_1': random(),
        'CD2_2': random(),
        'CTYPE1': 'RA---TAN',
        'CTYPE2': 'DEC--TAN',
        'CRPIX1': 512.0,
        'CRPIX2': 512.0,
        'CRVAL1': 180.0,
        'CRVAL2': -30.0
    }
    
    wcs = WCS(header)
    print(wcs)
    pprint(wcs)
    print("Sky angle:", wcs.sky_angle())
    print("Sky scale:", wcs.sky_scale())
    pprint(wcs)

    x,y = wcs.world_to_pixel(2,4)
    ra,dec=wcs.pixel_to_world(x,y)
    print(x,y)
    print(ra,dec)