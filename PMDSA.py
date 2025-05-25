from photutils.detection import DAOStarFinder
from stats import sigma_clipped_stats
from measure import measure, Star
import matplotlib.pyplot as plt
from FITS import fits
import numpy as np
import sys
import os


def show_2d_image(data: np.ndarray, file: fits.FITS):
    """
    Display a 2D image from the FITS file data using matplotlib.

    Parameters:
        data (np.ndarray): The 2D image data to display.
        file (fits.FITS): The FITS file object containing the image data.
    """
    plt.figure()  # Open a new figure window
    img=plt.imshow(data, cmap='gray', origin='lower')
    plt.colorbar(img, label='Pixel Intensity')  # Pass the variable to colorbar
    #plt.scatter([x1 - x_min, x2 - x_min], [y1 - y_min, y2 - y_min], color='red', s=10, label='Detected Stars')
    plt.title(f"Image of System {os.path.basename(os.path.dirname(file.filename))}")
    plt.xlabel("X (pixels)")
    plt.ylabel("Y (pixels)")
    #plt.legend()
    plt.show()

def find_stars(fits_file: fits.FITS):
    """
    Find stars in the FITS file data using DAOStarFinder.
    
    Parameters:
        fits_file (fits.FITS): The FITS file object containing the image data.
    
    Returns:
        list: A list of detected star sources.
    """
    mean, median, std = sigma_clipped_stats(fits_file.data, sigma=3.0)
    daofind = DAOStarFinder(fwhm=3.0, threshold=5.0 * std)
    sources = daofind(fits_file.data - median)
    
    if sources is None:
        print("No stars found.")
        return []
    
    return sources

def isolate_binary(fits_file: fits.FITS, sources):
    """
    Isolate the two brightest stars from the detected sources.
    
    Parameters:
        fits_file (fits.FITS): The FITS file object containing the image data.
        sources (list): List of detected star sources.
    
    Returns:
        tuple: Coordinates and fluxes of the two brightest stars.
    """
    # Sort sources by brightness
    sources.sort('flux')
    brightest = sources[::-1][:2]  # Take the two brightest sources

    if len(brightest) < 2:
        print("Error: Fewer than two stars detected.")
        return None, None, None, None

    # Extract pixel coordinates
    x1, y1 = brightest[0]['xcentroid'], brightest[0]['ycentroid']
    x2, y2 = brightest[1]['xcentroid'], brightest[1]['ycentroid']
    flux1, flux2 = brightest[0]['flux'], brightest[1]['flux']

    return Star(x1, y1, flux1), Star(x2, y2, flux2)

############
# MAIN RUN #
############
if __name__=='__main__':
    
    FILE = open(sys.argv[1], 'rb')
    fits_file = fits.FITS(FILE)

    #show_2d_image(fits_file.data, fits_file)

    sources = find_stars(fits_file)
    star1, star2 = isolate_binary(fits_file, sources)

    m= measure(fits_file.wcs)

    sep = m.separation(star1, star2)

    angle = m.position_angle(star1, star2)

    dmag = m.delta_mag(star1, star2)

    print(f"{sep:.2f},{angle:.2f},{dmag:.2f}")