# src/visionedgefusion/v1/core.py

import cv2
import numpy as np
from scipy.ndimage import gaussian_filter
from skimage.feature import hog
from typing import Tuple, Optional


def difference_of_gaussians(
    image: np.ndarray,
    low_sigma: float,
    high_sigma: Optional[float] = None,
    k: float = 1.6,
) -> np.ndarray:
    """
    Applies the Difference of Gaussians (DoG) algorithm to an image for edge/blob detection.

    Args:
        image (np.ndarray): The input image (can be color or grayscale).
        low_sigma (float): The standard deviation of the narrower Gaussian kernel.
        high_sigma (Optional[float]): The standard deviation of the wider Gaussian kernel.
                                       If None, it is calculated as low_sigma * k.
        k (float): The scaling factor between the two sigmas if high_sigma is not provided.

    Returns:
        np.ndarray: The resulting DoG image, highlighting edges and blobs.
    """
    if image.ndim == 3:
        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        image_gray = image

    if high_sigma is None:
        high_sigma = low_sigma * k

    if low_sigma > high_sigma:
        raise ValueError("low_sigma must be less than or equal to high_sigma.")

    # Apply Gaussian filters
    blur_low = gaussian_filter(image_gray, sigma=low_sigma)
    blur_high = gaussian_filter(image_gray, sigma=high_sigma)

    # Compute the difference
    dog_image = blur_low - blur_high

    return dog_image


def histogram_of_oriented_gradients(
    image: np.ndarray,
    orientations: int = 9,
    pixels_per_cell: Tuple[int, int] = (8, 8),
    cells_per_block: Tuple[int, int] = (2, 2),
    visualize: bool = False,
) -> np.ndarray:
    """
    Computes the Histogram of Oriented Gradients (HOG) feature descriptor for an image.

    This function is a wrapper around the scikit-image HOG implementation, providing a
    simplified interface for a common use case.

    Args:
        image (np.ndarray): The input image (can be color or grayscale). It will be resized
                            to a standard size (e.g., 128x64) for consistency.
        orientations (int): The number of orientation bins.
        pixels_per_cell (Tuple[int, int]): The size (in pixels) of a cell.
        cells_per_block (Tuple[int, int]): The number of cells in each block.
        visualize (bool): If True, returns a visualization of the HOG image as the second
                          element of a tuple.

    Returns:
        np.ndarray or Tuple[np.ndarray, np.ndarray]:
            - If visualize is False, returns the HOG feature vector.
            - If visualize is True, returns a tuple of (HOG feature vector, HOG visualization image).
    """
    if image.ndim == 3:
        # HOG is typically performed on grayscale images
        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        image_gray = image

    # HOG descriptors are often computed on a fixed-size patch.
    # We resize the input image for a more consistent feature vector length.
    resized_img = cv2.resize(image_gray, (64, 128))

    hog_features, hog_image = hog(
        resized_img,
        orientations=orientations,
        pixels_per_cell=pixels_per_cell,
        cells_per_block=cells_per_block,
        visualize=True,
        block_norm="L2-Hys",
        feature_vector=True,
    )

    if visualize:
        return (hog_features, hog_image)
    else:
        return hog_features
