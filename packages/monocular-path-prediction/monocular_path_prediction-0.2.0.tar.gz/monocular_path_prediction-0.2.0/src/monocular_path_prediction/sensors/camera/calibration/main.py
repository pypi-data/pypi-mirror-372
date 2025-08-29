"""Camera calibration tools for the monocular path prediction pipeline."""

from loguru import logger

from monocular_path_prediction.config.definitions import (
    CameraCalibrationConfig,
    SerialConfig,
)
from monocular_path_prediction.config.setup_logger import setup_logger
from monocular_path_prediction.sensors.camera import map_cameras_to_indices
from monocular_path_prediction.sensors.camera.calibration.calibration import (
    CameraCalibration,
)
from monocular_path_prediction.sensors.camera.camera import Camera
from monocular_path_prediction.sensors.device import Selector, find_serial_devices


def main() -> None:
    """Run the calibration CLI."""
    imu_selector = Selector()
    port_info = imu_selector.select_interactive(device_finder=find_serial_devices)
    if port_info is not None:
        imu_config = SerialConfig(port=port_info.name)
    else:
        imu_config = None
    setup_logger(filename="camera_calibration")

    cam_selector = Selector()
    camera_info = cam_selector.select_interactive(device_finder=map_cameras_to_indices)
    if camera_info is None:
        logger.error("No camera selected. Exiting.")
    else:
        camera = Camera(camera_info)
        config = CameraCalibrationConfig()
        cal_session = CameraCalibration(
            camera=camera, imu_config=imu_config, config=config
        )
        cal_session.run()


if __name__ == "__main__":  # pragma: no cover
    main()
