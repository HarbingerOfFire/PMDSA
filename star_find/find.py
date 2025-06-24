from numpy.lib.stride_tricks import sliding_window_view
import matplotlib.pyplot as plt
import numpy as np
from . import edge

''''''

def median_filter_numpy(arr, size=3):
    """    Apply a median filter to a 2D numpy array using sliding window view.
    Parameters:
        arr (np.ndarray): Input 2D array.
        size (int): Size of the square window.

    Returns:
        np.ndarray: Median filtered array.
    """
    arr_padded = np.pad(arr, size // 2, mode='reflect')
    windows = sliding_window_view(arr_padded, (size, size))
    return np.median(windows, axis=(-2, -1))

class StarFinder:
    """
    A class for finding stars in an image using median filtering and edge detection.
    """

    def __init__(self, sigma: float = 1.0, window_size: int = 3):
        """
        Initialize the StarFinder with a Gaussian blur sigma and median filter window size.
        """
        self.sigma = sigma
        self.window_size = window_size
        self.stars = []

    def find_stars(self, image: np.ndarray) -> np.ndarray:
        """
        Find stars in the given image by applying a median filter and edge detection.
        
        Parameters:
            image (np.ndarray): Input image array.

        Returns:
            np.ndarray: Coordinates of detected stars.
        """
        filtered = median_filter_numpy(image)
        ed = edge.EdgeDetector(sigma=self.sigma)
        edges_grad = ed.detect_edges(filtered)

        result = self.local_minima_sliding_window(edges_grad, X=2.0)
        minima_coords = np.argwhere(result) + 1  # Adjust for the sliding window
        return minima_coords

    def local_minima_sliding_window(self, data: np.ndarray, X: float) -> np.ndarray:
        """
        Find local minima in a 2D array using a sliding window approach.
        
        Parameters:
            data (np.ndarray): Input 2D array.
            X (float): Multiplier for the threshold based on mean and standard deviation.

        Returns:
            np.ndarray: Boolean array indicating local minima positions.
        """
        mean = np.mean(data)
        sigma = np.std(data)
        threshold = mean + X * sigma

        # Mask: region must be above threshold
        mask = data > threshold

        # Extract 3x3 windows for every valid position
        windows = sliding_window_view(data, (3, 3))

        # The center pixel in each window
        center = windows[:, :, 1, 1]

        # Compare center pixel to all other 8 elements in the window
        w_flat = windows.reshape(*center.shape, 9)

        # 8 neighbors are indices != 4
        neighbors = np.delete(w_flat, 4, axis=-1)

        # True if center < all neighbors
        local_min = np.all(center[..., None] < neighbors, axis=-1)

        # Mask must be cropped to match window result shape
        cropped_mask = mask[1:-1, 1:-1]

        # Only keep local minima that are in the high-signal regions
        result = np.logical_and(local_min, cropped_mask)

        return result
    
    def sum_within_radius(self, array: np.ndarray, cx: int, cy: int, radius: float) -> float:
        """
        Sum values within a circular region of a given radius around a center point.
        
        Parameters:
            array (np.ndarray): Input 2D array.
            cx (int): X coordinate of the center.
            cy (int): Y coordinate of the center.
            radius (float): Radius of the circular region.

        Returns:
            float: Sum of values within the circular region.
        """
        ny, nx = array.shape
        y, x = np.ogrid[:ny, :nx]
        dist_sq = (x - cx)**2 + (y - cy)**2
        mask = dist_sq <= radius**2
        return np.sum(array[mask])
    
    def analyze_stars(self, image: np.ndarray, minima_coords: np.ndarray, ref_point: tuple = None) -> list:
        """
        Analyze detected stars to compute their properties.

        Parameters:
            image (np.ndarray): Input image array.
            minima_coords (np.ndarray): Coordinates of detected stars.
            ref_point (tuple, optional): Reference point (x, y) to compute distances from.
                                         Defaults to image center if not provided.

        Returns:
            list: List of star properties including coordinates and local sky background.
        """
        ny, nx = image.shape
        y, x = np.ogrid[:ny, :nx]
        sky_radius = 3  # Radius for local sky background estimation

        # Set reference point to center if not provided
        if ref_point[0] is None:
            ref_x, ref_y = nx // 2, ny // 2
        else:
            ref_x, ref_y = ref_point

        for cy, cx in minima_coords:
            dist_sqr = (x - cx)**2 + (y - cy)**2
            mask = dist_sqr <= sky_radius**2
            local_patch = image[mask]

            mean = np.mean(local_patch)
            median = np.median(local_patch)
            sky_value = (2 * median) - mean

            star_radius = 1
            max_radius = 50  # safeguard
            while star_radius < max_radius:
                x_min = max(int(cx - star_radius), 0)
                x_max = min(int(cx + star_radius) + 1, nx)
                y_min = max(int(cy - star_radius), 0)
                y_max = min(int(cy + star_radius) + 1, ny)

                y_indices, x_indices = np.ogrid[y_min:y_max, x_min:x_max]
                distance_sq = (x_indices - cx)**2 + (y_indices - cy)**2
                mask = distance_sq <= star_radius**2
                values_in_circle = image[y_min:y_max, x_min:x_max][mask]

                if np.any(values_in_circle <= sky_value):
                    flux = self.sum_within_radius(image, cx, cy, star_radius)
                    dist = np.sqrt((cx - ref_x) ** 2 + (cy - ref_y) ** 2)
                    self.stars.append((cx, cy, flux, star_radius, dist))
                    break

                star_radius += 1

        # Sort stars by distance from the reference point
        self.stars.sort(key=lambda star: star[4])  # Sort by distance
        return self.stars

    def plot_star_zoom(self, image, star, zoom_factor=4, title="Star Zoom"):
        """
        Plot a zoomed-in region around a star.

        Parameters:
            image (np.ndarray): The full image array.
            star (tuple): Star tuple (cx, cy, flux, aperture, dist).
            zoom_factor (float): Multiplier for the aperture to define zoom window.
            title (str): Plot title.
        """
        cy, cx, aperture = star.y, star.x, star.aperture_radius
        radius = int(np.ceil(aperture * zoom_factor))
        ny, nx = image.shape
        x_min = max(int(cx - radius), 0)
        x_max = min(int(cx + radius) + 1, nx)
        y_min = max(int(cy - radius), 0)
        y_max = min(int(cy + radius) + 1, ny)
        zoom_img = image[y_min:y_max, x_min:x_max]

        plt.figure(figsize=(5, 5))
        plt.imshow(zoom_img, cmap='gray', origin='lower',
                   extent=[x_min, x_max, y_min, y_max])
        plt.title(title)
        plt.colorbar()
        plt.axis('on')
        plt.show()

    def plot_star_zoom_3d(self, image, star, zoom_factor=4, title="Star Zoom 3D"):
        """
        Plot a 3D surface zoomed-in region around a star.

        Parameters:
            image (np.ndarray): The full image array.
            star (tuple): Star tuple (cx, cy, flux, aperture, dist).
            zoom_factor (float): Multiplier for the aperture to define zoom window.
            title (str): Plot title.
        """
        cy, cx, aperture = star.y, star.x, star.aperture_radius
        radius = int(np.ceil(aperture * zoom_factor))
        ny, nx = image.shape
        x_min = max(int(cx - radius), 0)
        x_max = min(int(cx + radius) + 1, nx)
        y_min = max(int(cy - radius), 0)
        y_max = min(int(cy + radius) + 1, ny)
        zoom_img = image[y_min:y_max, x_min:x_max]

        x = np.arange(x_min, x_max)
        y = np.arange(y_min, y_max)
        X, Y = np.meshgrid(x, y)

        fig = plt.figure(figsize=(7, 5))
        ax = fig.add_subplot(111, projection='3d')
        ax.plot_surface(X, Y, zoom_img, cmap='inferno', edgecolor='none')
        ax.set_title(title)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Intensity')
        plt.show()
