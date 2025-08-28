import numpy as np
from scipy.optimize import curve_fit

def gaussian_2d(coords, A, x0, y0, sigma_x, sigma_y, B):
    x, y = coords
    return (A * np.exp(
        -(((x - x0) ** 2) / (2 * sigma_x ** 2) + ((y - y0) ** 2) / (2 * sigma_y ** 2))
    ) + B).ravel()

def fit_gaussian(image):
    y = np.arange(image.shape[0])
    x = np.arange(image.shape[1])
    x, y = np.meshgrid(x, y)

    A_init = np.max(image) - np.min(image)
    x0_init = image.shape[1] / 2
    y0_init = image.shape[0] / 2
    sigma_x_init = image.shape[1] / 4
    sigma_y_init = image.shape[0] / 4
    B_init = np.min(image)

    initial_guess = (A_init, x0_init, y0_init, sigma_x_init, sigma_y_init, B_init)

    popt, _ = curve_fit(gaussian_2d, (x, y), image.ravel(), p0=initial_guess)

    return popt


def fit_gaussian_roi(image, roi_size=100, downsample=1, meshgrid_cache={}):
    """
    Fit a 2D Gaussian to a small ROI around the brightest pixel.

    Parameters:
    - image: 2D numpy array (grayscale image)
    - roi_size: size of the square ROI (must be even-ish and small, e.g., 50-150)
    - downsample: integer factor to downsample the image for fitting
    - meshgrid_cache: dict to store cached meshgrids to avoid recomputation

    Returns:
    - params: (A, x0, y0, sigma_x, sigma_y, B) with coordinates scaled back to full-res
    """
    # Step 1: Find max pixel for ROI center
    max_y, max_x = np.unravel_index(np.argmax(image), image.shape)
    half = roi_size // 2
    y1, y2 = max(0, max_y - half), min(image.shape[0], max_y + half)
    x1, x2 = max(0, max_x - half), min(image.shape[1], max_x + half)
    cropped = image[y1:y2, x1:x2]

    # Step 2: Downsample if needed
    if downsample > 1:
        import cv2
        cropped = cv2.resize(cropped, (cropped.shape[1] // downsample, cropped.shape[0] // downsample),
                             interpolation=cv2.INTER_AREA)

    # Step 3: Meshgrid caching
    h, w = cropped.shape
    if (h, w) not in meshgrid_cache:
        y = np.arange(h)
        x = np.arange(w)
        meshgrid_cache[(h, w)] = np.meshgrid(x, y)
    xg, yg = meshgrid_cache[(h, w)]

    # Step 4: Initial guess
    A_init = np.max(cropped) - np.min(cropped)
    x0_init = w / 2
    y0_init = h / 2
    sigma_x_init = w / 4
    sigma_y_init = h / 4
    B_init = np.min(cropped)

    initial_guess = (A_init, x0_init, y0_init, sigma_x_init, sigma_y_init, B_init)

    # Step 5: Fit
    popt, _ = curve_fit(gaussian_2d, (xg, yg), cropped.ravel(), p0=initial_guess)

    # Step 6: Scale coordinates back to original image
    A, x0, y0, sigma_x, sigma_y, B = popt
    x0 = x1 + x0 * downsample
    y0 = y1 + y0 * downsample
    sigma_x *= downsample
    sigma_y *= downsample

    return (A, x0, y0, sigma_x, sigma_y, B)
