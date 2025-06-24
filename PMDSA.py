from measure import measure, Star
from star_find import find
from FITS import fits
import sys


############
# MAIN RUN #
############
if __name__=='__main__':
    
    #Load Header and WCS from File
    FILE = open(sys.argv[1], 'rb')
    try:
        ra, dec = float(sys.argv[2]), float(sys.argv[3])
    except IndexError: 
        ra, dec = None, None

    fits_file = fits.FITS(FILE)

    if ra and dec:
        x,y = fits_file.wcs.world_to_pixel(ra, dec)
    else: 
        x, y = None, None

    star_find = find.StarFinder(sigma=1.0, window_size=3)

    #Determine (X,Y) coordinates
    coords = star_find.find_stars(fits_file.data)

    #Identify Stars and Gather Flux information
    stars = star_find.analyze_stars(fits_file.data, coords, (x,y))

    if len(stars) < 2:
        print("Error: Fewer than two stars detected.")
        sys.exit(1)

    # Convert stars to Star objects
    # Assuming stars is a list of tuples (x, y, flux, aperture_radius, distance)
    star1, star2 = (Star(x, y, flux, aperture_radius, distance) for x, y, flux, aperture_radius, distance in stars[:2])    

    #Determine Position Angle, Seperation, and Differenetial Magnitude
    m= measure(fits_file.wcs)
    sep = m.separation(star1, star2)
    angle = m.position_angle(star1, star2)
    dmag = m.delta_mag(star1, star2)

    # plot the stars on the image (make true to see the plot)
    while False:
        star_find.plot_star_zoom(fits_file.data, star1)
        star_find.plot_star_zoom_3d(fits_file.data, star1)

    print(f"{sep:.2f},{angle:.2f},{dmag:.2f}")