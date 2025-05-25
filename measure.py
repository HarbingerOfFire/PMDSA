from math import radians, degrees, atan2, atan, sin, cos, sqrt, tan, asin
from dataclasses import dataclass
from FITS import fits
import numpy as np

'''
A module for measuring properties of stars in a FITS file using WCS.
This module provides a class `measure` that allows for the calculation of position angles,
separations, and magnitude differences between stars based on their pixel coordinates and flux values.
It uses the World Coordinate System (WCS) to convert pixel coordinates to celestial coordinates.
'''

@dataclass
class Star:
    '''
    A quick class to hold star data
    Attributes:
        x (float): X coordinate of the star in pixels
        y (float): Y coordinate of the star in pixels
        flux (float): Flux of the star, used for brightness calculations
    Methods:
        __repr__(): Returns a string representation of the Star object
    '''
    x: float
    y: float
    flux: float

    def __repr__(self):
        return f"Star(x={self.x}, y={self.y}, flux={self.flux})"

class measure:
    """
    A class to measure properties of stars in a FITS file using WCS.
    Attributes:
        wcs (fits.wcs): The WCS object containing the World Coordinate System information.
    Methods:
        position_angle(star1: Star, star2: Star) -> float:
            Calculate the position angle between two stars in degrees.
        separation(star1: Star, star2: Star) -> float:
            Calculate the separation between two stars in arcseconds.
        delta_mag(star1: Star, star2: Star) -> float:
            Calculate the difference in magnitude between two stars.
    """
    def __init__(self, wcs):
        self.wcs:fits.wcs = wcs

    def position_angle(self, star1: Star, star2: Star) -> float:
        """
        Calculate the position angle between two stars in degrees.
        The position angle is the angle from north to the line connecting the two stars,
        measured in the direction of increasing right ascension.
        Parameters:
            star1 (Star): The first star object.
            star2 (Star): The second star object.
        Returns:
            float: The position angle in degrees.
        """
        # Step 1: Shift relative to reference pixel
        dx1, dy1 = star1.x - self.wcs.CRPIX1, star1.y - self.wcs.CRPIX2
        dx2, dy2 = star2.x - self.wcs.CRPIX1, star2.y - self.wcs.CRPIX2

        # Step 2: Apply CD matrix
        xi1   = self.wcs.CD1_1 * dx1 + self.wcs.CD1_2 * dy1
        eta1  = self.wcs.CD2_1 * dx1 + self.wcs.CD2_2 * dy1
        xi2   = self.wcs.CD1_1 * dx2 + self.wcs.CD1_2 * dy2
        eta2  = self.wcs.CD2_1 * dx2 + self.wcs.CD2_2 * dy2

        # Step 3: Convert WCS reference coordinates to radians
        alpha0 = radians(self.wcs.CRVAL1)
        delta0 = radians(self.wcs.CRVAL2)

        # Step 4: Compute spherical coordinates for point 1
        rho1 = sqrt(xi1**2 + eta1**2)
        c1 = atan(rho1)
        delta1 = asin(cos(c1) * sin(delta0) + (eta1 * sin(c1) * cos(delta0)) / rho1)
        alpha1 = alpha0 + atan2(xi1 * sin(c1), rho1 * cos(delta0) * cos(c1) - eta1 * sin(delta0) * sin(c1))

        # Step 5: Compute spherical coordinates for point 2
        rho2 = sqrt(xi2**2 + eta2**2)
        c2 = atan(rho2)
        delta2 = asin(cos(c2) * sin(delta0) + (eta2 * sin(c2) * cos(delta0)) / rho2)
        alpha2 = alpha0 + atan2(xi2 * sin(c2), rho2 * cos(delta0) * cos(c2) - eta2 * sin(delta0) * sin(c2))

        # Step 6: Compute position angle from point 1 to point 2 (on celestial sphere)
        d_alpha = alpha2 - alpha1
        theta = atan2(
            sin(d_alpha),
            cos(delta1) * tan(delta2) - sin(delta1) * cos(d_alpha)
        )

        return degrees(theta)

    def separation(self, star1: Star,star2: Star) -> float:
        """
        Calculate the separation between two stars in arcseconds.
        The separation is the distance between the two stars in the sky,
        measured in arcseconds.
        Parameters:
            star1 (Star): The first star object.
            star2 (Star): The second star object.
        Returns:
            float: The separation in arcseconds.
        """
        dx = (star2.x-star1.x)*self.wcs.CDELT1*3600
        dy = (star2.y-star1.y)*self.wcs.CDELT2*3600

        return ((dx**2)+(dy**2))**0.5

    def delta_mag(self, star1: Star, star2: Star) -> float:
        """
        Calculate the difference in magnitude between two stars.
        The difference in magnitude is calculated using the formula:
        Δm = -2.5 * log10(F1/F2)
        where F1 and F2 are the fluxes of the two stars.
        Parameters:
            star1 (Star): The first star object.
            star2 (Star): The second star object.
        Returns:
            float: The difference in magnitude between the two stars.
        """
        if star1.flux <= 0 or star2.flux <= 0:
            raise ValueError("Flux values must be positive for magnitude calculation.")
        return abs(-2.5 * np.log10(star1.flux/star2.flux))