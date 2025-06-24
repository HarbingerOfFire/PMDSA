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

from math import atan2, degrees, radians, cos, sin

class WCS:
    def __init__(self, header):
        self.header = header
        self.CD1_1 = float(header['CD1_1'])
        self.CD1_2 = float(header['CD1_2'])
        self.CD2_1 = float(header['CD2_1'])
        self.CD2_2 = float(header['CD2_2'])

        self.WCS = [[self.CD1_1, self.CD1_2], 
                   [self.CD2_1, self.CD2_2]]

        self.CTYPE1 = header['CTYPE1']
        self.CTYPE2 = header['CTYPE2']

        self.CRPIX1 = float(header['CRPIX1'])
        self.CRPIX2 = float(header['CRPIX2'])

        self.CRVAL1 = float(header['CRVAL1'])
        self.CRVAL2 = float(header['CRVAL2'])
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
            f"  'CROTA2': {getattr(self, 'CROTA2', None)!r},\n"
            f"  'CDELT1': {getattr(self, 'CDELT1', None)!r},\n"
            f"  'CDELT2': {getattr(self, 'CDELT2', None)!r}\n"
            "}"
        )

    def __str__(self):
        return f"{self.__class__.__name__}({self.WCS})"

    def sky_angle(self):
        """
        Get the angle of the sky in degrees
        To retrieve in radians, use radians(sky_angle())
        Sets CROTA2 for future refrence
        """
        self.CROTA2 = degrees(atan2(self.CD2_1, self.CD1_1))
        assert hasattr(self, 'CROTA2'), "CROTA2 not set"
        return self.CROTA2
    
    def sky_scale(self):
        """
        Get the scale of the sky in degrees per pixel
        To retrieve in arcseconds per pixel, multiply by 3600
        Sets CROTA2, CDELT1 and CDELT2 for future refrence
        """
        if not hasattr(self, 'CROTA2'):
            self.sky_angle()

        self.CDELT1 = self.CD1_1/cos(radians(self.CROTA2))
        self.CDELT2 = self.CD2_2/cos(radians(self.CROTA2))
        assert hasattr(self, 'CDELT1'), "CDELT1 not set"
        assert hasattr(self, 'CDELT2'), "CDELT2 not set"

        return self.CDELT1, self.CDELT2
    
    def world_to_pixel(self, RA:float, Dec:float):
        """
        Convert RA, Dec to pixel coordinates.
        Uses the WCS formula: pixel = (coord - CRVAL) / CDELT + CRPIX

        Parameters:
            RA (float): The RA/longitude of the target in degrees
            DEC (float): The DEC/latitude of the target in degrees
        
        Returns:
            tuple[float]: the pixel coordinate of the cooresponding RA/DEC as (x,y)
        """
        pix_x = (RA - self.CRVAL1) / self.CDELT1 + self.CRPIX1
        pix_y = (Dec - self.CRVAL2) / self.CDELT2 + self.CRPIX2
        return pix_x, pix_y
    
    def pixel_to_world(self, Pixel_x: float, Pixel_y:float): 
        """
        Convert Pixel coordinates to RA,DEC based on wcs
        Inverse of world_to_pixel

        Parameters:
            Pixel_x (float): the x coordinate in the image
            Pixel_y (float): the y coordinate in the image

        Returns: 
            tuple[float]: the (RA, DEC) of the pixel coordinate
        """
        RA  = (Pixel_x - self.CRPIX1)*self.CDELT1 + self.CRVAL1
        DEC = (Pixel_y - self.CRPIX2)*self.CDELT2 + self.CRVAL2
        return RA, DEC


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