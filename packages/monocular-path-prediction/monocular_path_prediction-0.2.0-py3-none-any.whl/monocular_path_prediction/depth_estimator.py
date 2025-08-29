"""Monocular depth and normal estimation algorithms."""

from typing import Optional

import cv2
import numpy as np
import torch
from depth_anything_v2.dpt import DepthAnythingV2
from loguru import logger

from monocular_path_prediction.config.definitions import (
    EPSILON,
    MODEL_CONFIGS,
    MODEL_EXTENSION,
    PRETRAINED_MODEL_DIR,
)


class MonocularDepthEstimator:
    """Class for estimating inverse depth maps from images."""

    def __init__(self, encoder: str, device: Optional[str] = None):
        if device is None:
            self.device = (
                "cuda"
                if torch.cuda.is_available()
                else "mps"
                if torch.backends.mps.is_available()
                else "cpu"
            )
        else:
            self.device = device
        logger.info(f"Using device: {self.device}")

        self.model = self.load_model(encoder)

    def load_model(self, encoder: str):
        """Load the model for the specified encoder."""
        checkpoint_path = (
            PRETRAINED_MODEL_DIR / f"depth_anything_v2_{encoder}{MODEL_EXTENSION}"
        )
        logger.info(f"Loading model for encoder: {encoder}")

        if not checkpoint_path.exists():
            msg = f"Checkpoint {checkpoint_path} not found."
            logger.error(msg)
            raise FileNotFoundError(msg)

        model = DepthAnythingV2(**MODEL_CONFIGS[encoder])
        model.load_state_dict(torch.load(checkpoint_path, map_location="cpu"))
        return model.to(self.device).eval()

    @staticmethod
    def _convert_to_bgr(image: np.ndarray) -> np.ndarray:
        """Convert RGB to BGR if needed (OpenCV uses BGR)."""
        if len(image.shape) == 3 and image.shape[2] == 3:
            # Check if an image is in RGB format (this is a heuristic)
            if image[0, 0, 0] > image[0, 0, 2]:  # If R > B, likely RGB
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        return image

    def infer_inverse_depth(self, image: np.ndarray) -> np.ndarray:
        """Infer an inverse depth map from an image.

        Args:
            image: a preloaded image as a numpy array

        Returns:
            Inverse depth map as a numpy array

        """
        # Convert RGB to BGR if needed (OpenCV uses BGR)
        image = self._convert_to_bgr(image)
        return self.model.infer_image(image)

    def infer_depth(self, image: np.ndarray) -> np.ndarray:
        """Infer an inverse depth map from an image."""
        inv_depth_map = self.infer_inverse_depth(image)
        depth = 1.0 / (inv_depth_map + EPSILON)
        return depth
