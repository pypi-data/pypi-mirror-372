"""Camera calibration tools for the monocular path prediction pipeline."""

from pathlib import Path

import numpy as np
from loguru import logger

from monocular_path_prediction.config.definitions import CameraCalibrationConfig
from monocular_path_prediction.sensors.camera.camera_intrinsics import CameraIntrinsics


class NPZStorage:
    """Persist calibration results to and from .npz files."""

    @staticmethod
    def save(result: CameraIntrinsics, path: Path) -> None:
        """Save a calibration result to a .npz file.

        :param Intrinsics result: Calibration results to persist.
        :param Path path: Output file path.
        """
        np.savez(
            path,
            mtx=result.camera_matrix,
            dist=result.dist_coeffs,
            image_size=result.image_size,
        )
        logger.info(f"Saved calibration to '{path}'.")

    @staticmethod
    def load(path: Path) -> CameraIntrinsics | None:
        """Load a calibration result from a .npz file.

        :param Path path: Input .npz path.
        :return: Loaded calibration result.
        :rtype: Intrinsics
        """
        if path.exists():
            logger.info(f"Loading camera calibration from '{path}'.")
            data = np.load(path, allow_pickle=True)
            return CameraIntrinsics(
                camera_matrix=data["mtx"],
                dist_coeffs=data["dist"],
                image_size=tuple(data["image_size"]),
            )
        else:
            logger.warning(f"No camera calibration found at '{path}'.")
            return None


def get_calibration_filepath(camera_name: str) -> Path:
    """Return the calibration filepath."""
    filename = f"{camera_name}_calibration.npz"
    filepath = Path(CameraCalibrationConfig.save_dir) / filename
    return filepath
