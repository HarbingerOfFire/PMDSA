import numpy as np
from . import gauss

'''
A module for differential edge detection using guassian blur in star finding.
This module provides a class `EdgeDetector` that allows for the application of edge detection algorithms to np.ndarray images.
This is useful for identifying edges in images, which can help in detecting stars and other celestial objects.
'''
class EdgeDetector:
    def __init__(self, sigma: float):
        """
        Edge detector using your custom GaussianBlur.
        """
        self.blur = gauss.GaussianBlur(sigma)
        self.sigma = sigma

    def detect_edges(self, image: np.ndarray) -> np.ndarray:
        """
        Detect edges in the given image using Gaussian blur and gradient magnitude.
        """
        size = 2 * int(3 * self.sigma) + 1
        kernel = self.blur.gaussian_kernel(size)
        blurred = self.blur.apply(image, kernel)

        # Approximate gradient magnitude
        kernel_dx = np.array([[1, 0, -1]])
        kernel_dy = kernel_dx.T
        grad_x = self.blur.apply(blurred, kernel_dx)
        grad_y = self.blur.apply(blurred, kernel_dy)
        edges = np.hypot(grad_x, grad_y)

        # Normalize to [0, 1]
        edges = (edges - edges.min()) / (edges.max() - edges.min())
        return edges

