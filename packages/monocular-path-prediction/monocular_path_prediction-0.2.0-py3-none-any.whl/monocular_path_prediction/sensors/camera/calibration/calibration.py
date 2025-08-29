"""Camera calibration tools for the monocular path prediction pipeline."""

import sys
import time

import cv2
from loguru import logger
from numpy.typing import NDArray
from scipy.spatial.transform import Rotation as Rot

from monocular_path_prediction.config.definitions import (
    ESCAPE_KEY,
    SPACE_KEY,
    CameraCalibrationConfig,
    Colors,
    SerialConfig,
)
from monocular_path_prediction.sensors.camera.calibration.detector import (
    ChessboardDetector,
)
from monocular_path_prediction.sensors.camera.calibration.results import (
    NPZStorage,
    get_calibration_filepath,
)
from monocular_path_prediction.sensors.camera.camera import Camera
from monocular_path_prediction.sensors.camera.camera_intrinsics import CameraIntrinsics
from monocular_path_prediction.sensors.imu.imu import IMUDevice

LOOP_SLEEP_TIME_SEC = 1 / 30


class CameraCalibration:
    """Orchestrate capture, detection, and calibration."""

    def __init__(
        self,
        camera: Camera,
        config: CameraCalibrationConfig | None = None,
        detector: ChessboardDetector | None = None,
        imu_config: SerialConfig | None = None,
    ) -> None:
        """Initialize the session.

        :param CameraCalibrationConfig config: Runtime configuration.
        :param Camera camera: Camera source abstraction.
        :param ChessboardDetector detector: ChessboardDetector detector.
        """
        self.camera = camera

        if config is None:
            config = CameraCalibrationConfig()
        self.config = config

        if detector is None:
            detector = ChessboardDetector(
                checkerboard=config.checkerboard, square_size=config.square_size_meters
            )
        self.detector = detector
        logger.info(f"Camera calibration checkerboard: {config}")

        self._obj_points: list[NDArray] = []
        self._img_points: list[NDArray] = []
        self._imu_poses: list[NDArray] = []
        self._last_gray_shape: tuple[int, int] | None = None

        self._count: int = 0

        if imu_config is not None:
            imu = IMUDevice(config=imu_config)
            imu.open()
        else:
            imu = None
            logger.warning(
                "No IMU configuration provided. Unable to find IMU to Camera alignment."
            )
        self.imu: IMUDevice | None = imu

    def _capture_loop(self) -> None:
        """Capture frames and collect detections until the quota is met."""
        logger.info("Press SPACE to capture a detection; ESC to finish early.")

        while self._count < self.config.capture_count:
            if self.imu is not None:
                imu_data, pose = self.imu()
            else:
                pose = None
            frame = self.camera.capture_frame()
            if frame is None:
                # Avoid log spam on transient read failures
                time.sleep(LOOP_SLEEP_TIME_SEC)
                continue

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            self._last_gray_shape = gray.shape[::-1]  # (width, height)
            found, corners = self.detector.detect(gray)

            self._show_frame(frame, corners, found)

            key = cv2.waitKey(1)
            if key == ESCAPE_KEY:
                logger.warning("Early exit requested.")
                break

            if found and corners is not None and key == SPACE_KEY:
                self._record_detection(corners=corners, imu_pose=pose)
                self._save_frame(frame)
                self._count += 1

        self._close_frame()
        self._check_number_images_captured()

    def _save_frame(self, frame: NDArray) -> None:
        """Save a frame to disk."""
        out_path = self.config.save_dir / f"calib_{self._count:02}.png"
        cv2.imwrite(str(out_path), frame)
        logger.info(f"Captured frame {self._count + 1} at {out_path}")

    def _record_detection(self, corners: NDArray, imu_pose: NDArray | None) -> None:
        """Record a detection and its corresponding image points."""
        self._obj_points.append(self.detector.obj_points_template.copy())
        self._img_points.append(corners)
        if imu_pose is not None:
            self._imu_poses.append(imu_pose)

    def _show_frame(self, frame: NDArray, corners: NDArray | None, found: bool) -> None:
        preview = frame.copy()
        if found and corners is not None:
            cv2.drawChessboardCorners(
                preview, self.detector.checkerboard, corners, found
            )
        cv2.putText(
            preview,
            f"Captured: {self._count}/{self.config.capture_count}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=0.7,
            color=Colors.green,
            thickness=2,
        )
        cv2.imshow("Camera Calibration (Space button to capture frame)", preview)

    @staticmethod
    def _close_frame() -> None:
        """Close the frame window."""
        cv2.destroyAllWindows()
        cv2.waitKey(1)

    def _check_number_images_captured(self) -> None:
        """Check that enough images have been captured."""
        min_images = self.config.capture_count_min
        if len(self._img_points) < min_images:
            logger.error(
                f"Not enough valid captures for calibration (need >= {min_images})."
            )
            raise SystemExit(1)

    def run(self) -> None:
        """Run a full calibration session (capture → detect → calibrate).

        :raises SystemExit: If the camera cannot open or calibration fails.
        """
        self.config.save_dir.mkdir(parents=True, exist_ok=True)
        try:
            self._capture_loop()
        except KeyboardInterrupt:
            logger.warning("Early exit requested.")
            sys.exit(1)
        finally:
            self.camera.cleanup()

        assert self._last_gray_shape is not None, "Missing image size for calibration."

        ret, mtx, dist, r_vecs, t_vecs = cv2.calibrateCamera(
            self._obj_points,
            self._img_points,
            imageSize=self._last_gray_shape,  # (width, height)
            cameraMatrix=None,
            distCoeffs=None,
        )

        # TODO: find the SE3 matrix that aligns the camera and IMU frames.
        if len(self._imu_poses) == 0:
            logger.warning("No IMU poses found.")
        else:
            camera_frames = r_vecs_to_matrices(r_vecs=r_vecs)
            imu_frames = self._imu_poses
            solve_camera_frame_to_imu_frame(
                camera_frames=camera_frames, imu_frames=imu_frames
            )

        if not ret:
            logger.error("Calibration failed (cv2.calibrateCamera returned falsy).")
            raise SystemExit(1)

        result = CameraIntrinsics(
            camera_matrix=mtx,
            dist_coeffs=dist,
            image_size=self._last_gray_shape,
        )
        self._save_result(result)
        self._print_result(result)
        logger.info(f"Distortion coefficients: {result.dist_coeffs.ravel()}")
        logger.success("Calibration complete.")

    @staticmethod
    def _print_result(result: CameraIntrinsics) -> None:
        """Print the calibration result to the console."""
        logger.info("Camera values")
        K = result.camera_matrix
        logger.info(f"fx: {float(K[0, 0]):.2f}")
        logger.info(f"fy: {float(K[1, 1]):.2f}")
        logger.info(f"cx: {float(K[0, 2]):.2f}")
        logger.info(f"cy: {float(K[1, 2]):.2f}")
        logger.info(f"skew: {float(K[0, 1]):.2f}")

    @staticmethod
    def _print_result_difference(
        result_new: CameraIntrinsics, result_old: CameraIntrinsics
    ) -> None:
        """Print the calibration result to the console."""
        k_new = result_new.camera_matrix
        k_old = result_old.camera_matrix
        logger.warning(f"fx:   {float(k_old[0, 0]):.2f} -> {float(k_new[0, 0]):.2f}")
        logger.warning(f"fy:   {float(k_old[1, 1]):.2f} -> {float(k_new[1, 1]):.2f}")
        logger.warning(f"cx:   {float(k_old[0, 0]):.2f} -> {float(k_new[0, 2]):.2f}")
        logger.warning(f"cy:   {float(k_old[1, 2]):.2f} -> {float(k_new[1, 2]):.2f}")
        logger.warning(f"skew: {float(k_old[0, 1]):.2f} -> {float(k_new[0, 1]):.2f}")

    def _save_result(self, result: CameraIntrinsics) -> None:
        """Save the calibration result to disk."""
        yes_str = "y"
        no_str = "N"
        filepath = get_calibration_filepath(camera_name=self.camera.info.name)
        if filepath.exists():
            logger.warning(f"Calibration result already exists at {filepath}.")
            result_old = NPZStorage.load(filepath)
            if result_old is not None:
                self._print_result_difference(result_new=result, result_old=result_old)
            if input(f"Overwrite? ({yes_str}/{no_str}) ") != yes_str:
                logger.warning("Aborted calibration.")
                return
        NPZStorage.save(result, filepath)


def solve_camera_frame_to_imu_frame(
    camera_frames: list[NDArray], imu_frames: list[NDArray]
) -> bool:
    """Align the camera and IMU frames."""
    # TODO: finish these functions
    for cam_frame, imu_frame in zip(camera_frames, imu_frames):
        logger.debug(f"Camera pose:\n{cam_frame}")
        logger.debug(f"IMU pose:\n{imu_frame}")
    return True


def r_vec_to_matrix(r_vec: NDArray) -> NDArray:
    """Convert roll, pitch, yaw angles (radians) to a 3x3 rotation matrix.

    :param r_vec: Rotation vector in radians
    :return: 3x3 rotation matrix
    """
    # Convention: intrinsic rotations about x, y, z (roll-pitch-yaw)
    roll, pitch, yaw = r_vec
    rot = Rot.from_euler("xyz", [roll, pitch, yaw])
    return rot.as_matrix()


def r_vecs_to_matrices(r_vecs: list[NDArray]) -> list[NDArray]:
    """Convert roll, pitch, yaw angles (radians) to a 3x3 rotation matrix."""
    matrices = []
    for r_vec in r_vecs:
        rot_matrix = r_vec_to_matrix(r_vec=r_vec.ravel())
        matrices.append(rot_matrix)
    return matrices
