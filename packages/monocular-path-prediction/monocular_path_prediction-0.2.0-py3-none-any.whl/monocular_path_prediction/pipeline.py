"""Monocular Surface Normal Estimation Script."""

import sys
from pathlib import Path

import numpy as np
from loguru import logger
from numpy.typing import NDArray
from PIL import Image

from monocular_path_prediction import (
    MonocularDepthEstimator,
    PointCloudGenerator,
)
from monocular_path_prediction.config.definitions import PipelineConfig
from monocular_path_prediction.config.setup_logger import setup_logger
from monocular_path_prediction.sensors.camera import (
    Camera,
    Display,
    save_image,
)
from monocular_path_prediction.sensors.imu.imu import IMUDevice
from monocular_path_prediction.sensors.setup import setup_camera, setup_imu


class Pipeline:
    """Main class for running monocular surface normal estimation."""

    def __init__(self, config: PipelineConfig):
        self.log_filepath: Path = setup_logger(
            filename="pipeline",
            stderr_level=config.log_level,
            log_level=config.log_level,
            log_dir=config.output_dir,
        )

        self.config = config
        self.config.output_dir.mkdir(parents=True, exist_ok=True)

        self.depth_estimator = MonocularDepthEstimator(self.config.model_size)
        self.camera: Camera | None = None
        self.imu: IMUDevice | None = None
        self.display: Display = Display()

        # TODO - add microcontroller setup

    def setup(self) -> None:
        """Initialize camera and IMU."""
        logger.info("Setting up pipeline...")

        self.imu = setup_imu(imu_config=self.config.imu_config)
        self.camera = setup_camera(camera_index=self.config.camera_index)

        logger.info("Pipeline setup complete.")

    def run_loop(self, image_path: Path | None) -> None:
        """Run the pipeline in a loop."""
        logger.info("Running pipeline in loop... Press Ctrl+C to exit.")
        while True:
            try:
                self.run(image_path=image_path)
            except KeyboardInterrupt:
                logger.info("Pipeline interrupted.")
                break
            except Exception as err:
                logger.error(f"Pipeline failed: {err}")

    def run(self, image_path: Path | None) -> bool:
        """Run the pipeline."""
        logger.debug("Running pipeline iteration.")
        try:
            if self.imu is None:
                msg = "No IMU device configured."
                logger.warning(msg)
                return False

            imu_data, camera_pose = self.imu.wait_for_data()

            image = self.load_image(image_path)
            self.display.add_frame(frame=image)

            run_algorithm = True
            if run_algorithm:
                self.run_algorithm(image=image, camera_pose=camera_pose)

            self.display.add_pose(pose=camera_pose)
            self.display.add_delta_time()
            self.display.show()

            save = False
            if save:
                save_image(self.display.frame, self.config.output_dir)

            return True

        except OSError as err:
            logger.error(f"Pipeline failed: {err}")
            self.close()
            sys.exit(1)
        except Exception as err:
            logger.error(f"Pipeline failed: {err}")
            return False

    def run_algorithm(self, image: NDArray, camera_pose: NDArray):
        """Run the pipeline algorithm."""
        depth_map = self.depth_estimator.infer_depth(image)

        # TODO - calculate focal length from camera calibration
        focal_length_px = 500.0
        stride = 30
        k = 20
        logger.warning(f"Focal length: {focal_length_px} px")

        point_cloud = PointCloudGenerator.from_depth_map(
            depth_map=depth_map, image=image, focal_length_px=focal_length_px
        )
        point_cloud.filter_by_distance(self.config.max_point_distance)
        point_cloud.down_sample(stride=stride)  # TODO - hardcoded
        point_cloud.rotate(rotation_matrix=camera_pose)  # TODO - hardcoded
        normals = point_cloud.estimate_normals(k=k)  # TODO - hardcoded
        point_cloud.rotate(rotation_matrix=camera_pose.T)

        # TODO - calculate foot placement
        # TODO - send result to microcontroller

        self.display.add_depth_map(
            depth_map=depth_map, max_distance=self.config.max_point_distance
        )
        self.display.add_surface_normals(
            surface_normals=normals,
            point_cloud=point_cloud,
            focal_length_px=focal_length_px,
            sample_rate=5,
        )

    def load_image(self, image_path: Path | None) -> NDArray:
        """Load an image from a path or either an image from a camera."""
        if image_path:
            image = np.array(Image.open(image_path))
        elif self.camera:
            image = self.camera.capture_frame()
        else:
            msg = "No image or camera initialized."
            logger.warning(msg)
            raise RuntimeError(msg)
        return image

    def close(self) -> None:
        """Close all resources cleanly."""
        logger.info("Shutting down pipeline...")
        if self.imu:
            self.imu.close()
        if self.camera:
            self.camera.cleanup()
        logger.success("Pipeline closed.")
