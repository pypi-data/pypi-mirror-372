"""Camera interface for recording and taking pictures using OpenCV."""

from __future__ import annotations

import cv2
from loguru import logger
from numpy.typing import NDArray

from monocular_path_prediction.config.definitions import DEFAULT_IMAGE_WIDTH
from monocular_path_prediction.sensors.camera.calibration.results import (
    NPZStorage,
    get_calibration_filepath,
)
from monocular_path_prediction.sensors.camera.camera_intrinsics import CameraIntrinsics
from monocular_path_prediction.sensors.camera.images.images import resize_image
from monocular_path_prediction.sensors.device.device_info import DeviceInfo
from monocular_path_prediction.utils import wait_for_not_none


class Camera:
    """Camera interface for recording and taking pictures using OpenCV."""

    def __init__(self, info: DeviceInfo):
        """Initialize the camera.

        :param DeviceInfo info: Camera info.
        """
        self.info: DeviceInfo = info

        calibration_filepath = get_calibration_filepath(camera_name=info.name)
        self.calibration: CameraIntrinsics | None = NPZStorage.load(
            path=calibration_filepath
        )
        self.cap: cv2.VideoCapture = self._initialize_camera()
        self.image_width = DEFAULT_IMAGE_WIDTH

        assert self.cap is not None, "Failed to initialize camera."

    def _initialize_camera(self) -> cv2.VideoCapture:
        """Try to initialize a camera from the given index.

        :return: An open and working VideoCapture object.
        :raises RuntimeError: If no usable camera is found.
        """
        index = self.info.index
        cap = cv2.VideoCapture(index)

        # Try reading a frame to confirm it's functional
        logger.info(f"Attempting to open camera at index {index}...")
        wait_for_not_none(prompt="Waiting for camera to initialize.", func=cap.read)
        ret, frame = cap.read()
        if not ret:
            cap.release()

        # Set resolution
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        logger.info(f"Camera initialized at index {index}: ({width}x{height})")

        return cap

    def capture_frame(self) -> NDArray | None:
        """Capture and return the current frame from the camera."""
        ret, frame = self.cap.read()
        if not ret or frame is None:
            logger.warning("Failed to read frame from camera.")
            return None
        return resize_image(frame, new_width=self.image_width)

    def cleanup(self) -> None:
        """Release resources."""
        self.cap.release()
        cv2.destroyAllWindows()
        logger.success("Camera released.")

    def __enter__(self):
        """Enter the context manager and return the camera instance."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager and clean up camera resources."""
        self.cleanup()
