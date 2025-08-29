"""Run the module to test out a camera."""

import cv2
from loguru import logger

from monocular_path_prediction.sensors.camera import Camera, map_cameras_to_indices
from monocular_path_prediction.sensors.camera.display import Display
from monocular_path_prediction.sensors.device.device_selector import Selector

if __name__ == "__main__":  # pragma: no cover
    picker = Selector()
    camera_info = picker.select_interactive(device_finder=map_cameras_to_indices)
    if camera_info is None:
        logger.error("No camera selected. Exiting.")
    else:
        camera = Camera(info=camera_info)
        displayer = Display()
        try:
            while True:
                frame = camera.capture_frame()
                displayer.add_frame(frame)
                displayer.add_delta_time()
                displayer.show()

        except KeyboardInterrupt:
            logger.warning("Interrupted by user.")
        finally:
            camera.cleanup()
            cv2.destroyAllWindows()
