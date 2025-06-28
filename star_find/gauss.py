import numpy as np

'''
A module for guassian blurring of images used for edge detection in star finding.
This module provides a class `GaussianBlur` that allows for the application of a Gaussian blur to np.ndarray images.
This is useful for reducing noise and detail in images, making it easier to detect stars and other celestial objects.
'''

class GaussianBlur:
    def __init__(self, sigma: float):
        """
        Initialize the GaussianBlur with a given standard deviation.
        """
        self.sigma = sigma

    def gaussian_kernel(self, size: int) -> np.ndarray:
        """
        Generate a square Gaussian kernel of given size.
        """
        ax = np.linspace(-(size // 2), size // 2, size)
        xx, yy = np.meshgrid(ax, ax)
        kernel = np.exp(-(xx**2 + yy**2) / (2. * self.sigma**2))
        kernel = kernel / (2 * np.pi * self.sigma**2)
        return kernel / np.sum(kernel)

    def apply(self, image: np.ndarray, kernel: np.ndarray) -> np.ndarray:
        """
        Apply the given Gaussian kernel to the input image via convolution.
        """
        kernel_h, kernel_w = kernel.shape
        pad_h = kernel_h // 2
        pad_w = kernel_w // 2

        padded_image = np.pad(image, ((pad_h, pad_h), (pad_w, pad_w)), mode='reflect')

        output = np.zeros_like(image)

        windows = np.lib.stride_tricks.sliding_window_view(padded_image, kernel.shape)
        output = np.einsum('ijkl,kl->ij', windows, kernel)
    
        return output

# Example usage
if __name__ == "__main__":
    # Test data
    img = np.random.rand(100, 100)

    # Create blur object
    blur = GaussianBlur(sigma=5)

    # Generate kernel
    kernel = blur.gaussian_kernel(size=5)

    # Apply blur
    result = blur.apply(img, kernel)

    from matplotlib import pyplot as plt
    
    def show_2d_image(data: np.ndarray):
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
        plt.title(f"Image of Data")
        plt.xlabel("X (pixels)")
        plt.ylabel("Y (pixels)")
        #plt.legend()
        plt.show()

    show_2d_image(img)
    show_2d_image(result)