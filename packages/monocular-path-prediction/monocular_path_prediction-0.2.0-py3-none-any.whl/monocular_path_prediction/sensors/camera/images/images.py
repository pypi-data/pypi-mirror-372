"""Camera interface for recording and taking pictures using OpenCV."""

from pathlib import Path

import cv2
import numpy as np
from loguru import logger
from numpy.typing import NDArray
from PIL import Image

from monocular_path_prediction.sensors.camera.camera_intrinsics import CameraIntrinsics
from monocular_path_prediction.utils import get_timestamped_filepath


def resize_image(image: NDArray, new_width: int) -> np.ndarray:
    """Resize an image to a target width while maintaining the same aspect ratio.

    Args:
        image: Input image as a numpy array
        new_width: Target width in pixels

    Returns:
        resized_image

    """
    h, w = image.shape[:2]
    scale_factor = new_width / w
    new_height = int(h * scale_factor)

    # Convert numpy array to PIL Image for resizing
    pil_image = Image.fromarray(image)
    resized_pil = pil_image.resize((new_width, new_height), Image.LANCZOS)
    resized_image = np.array(resized_pil)

    logger.debug(f"Image resized to {resized_image.shape}")

    return resized_image


def save_image(image: np.ndarray, output_dir: Path) -> Path:
    """Save an image to a file."""
    filepath = get_timestamped_filepath(
        output_dir=output_dir, suffix="jpg", prefix="img_"
    )
    cv2.imwrite(str(filepath), image)
    logger.info(f"Image saved: {filepath}")
    return filepath


def undistort_image(image: NDArray, calib: CameraIntrinsics | None) -> NDArray:
    """Return an undistorted copy of an image using the calibration.

    :param np.ndarray image: Input distorted image.
    :param CameraIntrinsics calib: Calibration results with intrinsics and distortion.
    :return: Undistorted image of the same size.
    :rtype: np.ndarray
    """
    if calib is None:
        return image.copy()
    h, w = image.shape[:2]
    new_camera_mtx, _ = cv2.getOptimalNewCameraMatrix(
        calib.camera_matrix, calib.dist_coeffs, (w, h), 1, (w, h)
    )
    return cv2.undistort(
        image, calib.camera_matrix, calib.dist_coeffs, None, new_camera_mtx
    )
