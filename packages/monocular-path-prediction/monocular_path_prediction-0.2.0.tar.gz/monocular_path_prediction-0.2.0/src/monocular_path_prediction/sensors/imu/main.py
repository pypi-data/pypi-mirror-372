"""Main file for testing the IMU device."""

import time

from loguru import logger

from monocular_path_prediction.sensors.device.device_selector import Selector
from monocular_path_prediction.sensors.device.serial_device import (
    SerialConfig,
    find_serial_devices,
)
from monocular_path_prediction.sensors.imu.imu import IMUDevice

if __name__ == "__main__":  # pragma: no cover
    """Test the IMU device."""
    imu_selector = Selector()
    device_info = imu_selector.select_interactive(device_finder=find_serial_devices)
    imu_config = SerialConfig(port=device_info.name)
    imu = IMUDevice(config=imu_config)

    try:
        imu.open()
        while True:
            data, pose = imu()
            time.sleep(1.0)
    except KeyboardInterrupt:
        logger.info("Interrupted.")
    except Exception as err:
        logger.error(f"Error occurred: {err}")
    finally:
        imu.close()
