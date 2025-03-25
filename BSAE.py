import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from astropy.io import fits
from astropy.stats import sigma_clipped_stats
from photutils.detection import DAOStarFinder
import sys, os

from astropy.wcs import WCS
from astropy.coordinates import SkyCoord
import astropy.units as u

# TODO 1: Suppress FITSFixedWarning
import warnings
from astropy.wcs.wcs import FITSFixedWarning
warnings.simplefilter("ignore", FITSFixedWarning)

def analyze_binary_star(fits_file, plot=False):
    # Load FITS file
    hdu = fits.open(fits_file)
    header = hdu[0].header
    data = hdu[0].data
    hdu.close()

    # Extract WCS information
    wcs = WCS(header)

    # Compute background statistics
    mean, median, std = sigma_clipped_stats(data, sigma=3.0)

    # Detect stars
    daofind = DAOStarFinder(fwhm=3.0, threshold=5.0 * std)
    sources = daofind(data - median)

    # Sort sources by brightness
    sources.sort('flux')
    brightest = sources[::-1][:2]  # Take the two brightest sources

    if len(brightest) < 2:
        print("Error: Fewer than two stars detected.")
        return None

    # Extract pixel coordinates
    x1, y1 = brightest[0]['xcentroid'], brightest[0]['ycentroid']
    x2, y2 = brightest[1]['xcentroid'], brightest[1]['ycentroid']
    flux1, flux2 = brightest[0]['flux'], brightest[1]['flux']

    # Convert pixel coordinates to RA/Dec
    sky1 = SkyCoord.from_pixel(x1, y1, wcs)
    sky2 = SkyCoord.from_pixel(x2, y2, wcs)

    # Compute separation in arcseconds
    separation = sky1.separation(sky2).arcsec

    # Compute correct position angle (North=0°, East=90°)
    position_angle = sky1.position_angle(sky2).deg

    # Compute magnitude difference
    delta_mag = abs(-2.5 * np.log10(flux1 / flux2))

    print(f"{separation:.2f},{position_angle:.2f},{delta_mag:.2f}")

    if plot:
        # Determine zoom-in region
        zoom_factor = 5
        zoom_size = max(separation * zoom_factor, 40)

        x_center, y_center = (x1 + x2) / 2, (y1 + y2) / 2
        x_min, x_max = int(x_center - zoom_size / 2), int(x_center + zoom_size / 2)
        y_min, y_max = int(y_center - zoom_size / 2), int(y_center + zoom_size / 2)

        # Ensure bounds stay within image limits
        x_min, x_max = max(0, x_min), min(data.shape[1], x_max)
        y_min, y_max = max(0, y_min), min(data.shape[0], y_max)

        # Extract zoomed-in region
        zoomed_data = data[y_min:y_max, x_min:x_max]

        # Adjust contrast dynamically
        vmin = np.min(zoomed_data)
        vmax = np.max(zoomed_data)

        # --- 2D Zoomed-in Plot ---
        plt.figure()  # Open a new figure window
        img=plt.imshow(zoomed_data, cmap='gray', origin='lower')
        plt.colorbar(img, label='Pixel Intensity')  # Pass the variable to colorbar
        plt.scatter([x1 - x_min, x2 - x_min], [y1 - y_min, y2 - y_min], color='red', s=10, label='Detected Stars')
        plt.title(f"Image of System {os.path.basename(os.path.dirname(fits_file))}")
        plt.xlabel("X (pixels)")
        plt.ylabel("Y (pixels)")
        plt.legend()
        plt.show()

        # --- 3D Surface Plot ---
        fig = plt.figure()  # Open a new figure window
        ax = fig.add_subplot(111, projection='3d')

        X, Y = np.meshgrid(np.arange(zoomed_data.shape[1]), np.arange(zoomed_data.shape[0]))
        ax.plot_surface(X, Y, zoomed_data, cmap='inferno', edgecolor=None)

        ax.set_title(f"3D Surface Plot of System {os.path.basename(os.path.dirname(fits_file))}")
        ax.set_xlabel("X (pixels)")
        ax.set_ylabel("Y (pixels)")
        ax.set_zlabel("Intensity")

        plt.show()

    return separation, position_angle, delta_mag

fits_file = sys.argv[1]
analyze_binary_star(fits_file, plot=True)
#ouputs the separation, position angle, and delta magnitude of the system in csv format
