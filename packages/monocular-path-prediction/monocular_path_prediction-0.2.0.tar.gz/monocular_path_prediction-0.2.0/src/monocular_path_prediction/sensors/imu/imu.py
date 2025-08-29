"""IMU device class compatible with resilient SerialDevice."""

from __future__ import annotations

import ast
import re
import threading
import time
from dataclasses import dataclass

from loguru import logger
from numpy.typing import NDArray
from py_imu.madgwick import Madgwick
from py_imu.quaternion import Vector3D
from scipy.spatial.transform import Rotation as Rot

from monocular_path_prediction.config.definitions import ImuConfig
from monocular_path_prediction.sensors.device.serial_device import (
    SerialConfig,
    SerialDevice,
)


@dataclass
class IMUData:
    """Represent parsed IMU data."""

    timestamp: float
    accel: Vector3D
    gyro: Vector3D
    mag: Vector3D | None = None


class IMUDevice(SerialDevice):
    """Parse IMU lines from a SerialDevice and maintain latest pose."""

    def __init__(self, config: SerialConfig | None = None):
        """Initialize IMU device and start parsing thread.

        The underlying SerialDevice opens and starts its background reader.
        We start an additional parser thread that consumes the newest line and
        updates the IMU pose via a Madgwick filter.
        """
        super().__init__(config=config)

        self.imu_config = ImuConfig()
        freq = 1.0 / self.imu_config.delta_time_sec
        self._madgwick = Madgwick(
            frequency=freq,
            gain=self.imu_config.madgwick_filter_gain,
        )

        self._latest_data: IMUData | None = None
        self.pose: NDArray | None = None
        self._previous_timestamp: float | None = None

        self._parser_thread = threading.Thread(
            target=self._parser_loop, name="IMUParser", daemon=True
        )
        self._parser_thread.start()

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def __call__(self) -> tuple[IMUData | None, NDArray | None]:
        """Return the latest parsed IMU data and pose (non-blocking)."""
        with self._lock:
            return self._latest_data, self.pose

    def stop(self) -> None:
        """Stop the parser thread and close serial."""
        self._state.running = False
        if self._parser_thread.is_alive():
            self._parser_thread.join(timeout=2.0)
        self.close()

    # Context manager override (optional sugar)
    def __exit__(self, exc_type, exc, tb) -> None:
        """Close the parser thread."""
        self.stop()

    # ------------------------------------------------------------------ #
    # Internal
    # ------------------------------------------------------------------ #
    def _parser_loop(self) -> None:
        """Continuously parse the newest serial line and update pose."""
        logger.info("IMU parser thread started.")
        last_line: str | None = None

        while self._state.running:
            try:
                # Get most recent line from SerialDevice (non-blocking)
                line = self.latest_line()
                if not line or line == last_line:
                    time.sleep(self.config.loop_delay)
                    continue

                last_line = line
                imu_data = self._parse_imu_line(line)
                if imu_data is None:
                    continue

                # Update filter + pose
                self._update_pose(imu_data)

            except Exception as err:
                # Keep running; SerialDevice will attempt reconnects underneath
                logger.warning(f"IMU parser error: {err}")
                time.sleep(1.0)

        logger.info("IMU parser thread exiting.")

    def _update_pose(self, imu_data: IMUData) -> None:
        """Update pose using the Madgwick filter with robust dt."""
        # Derive dt
        if self._previous_timestamp is None:
            dt = self.imu_config.delta_time_sec
            logger.debug(f"No previous timestamp; using default dt={dt:.4f}s.")
        else:
            dt = imu_data.timestamp - self._previous_timestamp
        self._previous_timestamp = imu_data.timestamp

        # Update filter
        self._madgwick.update(
            gyr=imu_data.gyro,
            acc=imu_data.accel,
            dt=dt,
        )
        q = self._madgwick.q  # x, y, z, w
        pose = Rot.from_quat(quat=[q.x, q.y, q.z, q.w], scalar_first=False).as_matrix()

        with self._lock:
            self._latest_data = imu_data
            self.pose = pose

        logger.debug(
            f"IMU: dt={dt:.4f}s, quat(xyzw)={q.x:.3f}, {q.y:.3f}, {q.z:.3f}, {q.w:.3f}"
        )

    def _parse_imu_line(self, line: str) -> IMUData | None:
        """Parse a line emitted by the IMU firmware.

        Expected format is defined by ImuConfig.time_pattern and meas_pattern.
        Example (conceptual):
            "t=123.456 <[(ax,ay,az),(gx,gy,gz)]>"
        """
        try:
            time_match = re.search(self.imu_config.time_pattern, line)
            meas_match = re.search(self.imu_config.meas_pattern, line)
            if not time_match or not meas_match:
                logger.debug(f"IMU line did not match patterns: {line}")
                return None

            timestamp = float(time_match.group(1))

            # measurements are expected to be a Python-literal list/tuple string
            measurements = ast.literal_eval(meas_match.group(1))
            if not measurements or not isinstance(measurements[0], tuple):
                logger.debug(f"Unexpected IMU measurement structure: {line}")
                return None

            accel_tuple, gyro_tuple = measurements[0]
            accel = Vector3D(*accel_tuple)
            gyro = Vector3D(*gyro_tuple)

            imu_data = IMUData(timestamp, accel, gyro)

            self._check_for_clipping(imu_data=imu_data)

            return imu_data

        except Exception as err:
            logger.debug(f"Failed to parse IMU line: {err} | line='{line}'")
            return None

    def _check_for_clipping(self, imu_data: IMUData) -> None:
        """Warn when any axis exceeds the configured max value."""
        signals = [imu_data.accel, imu_data.gyro]
        max_values = [self.imu_config.accel_range_gs, self.imu_config.gyro_range_rps]
        for signal, max_value in zip(signals, max_values):
            for v in (signal.x, signal.y, signal.z):
                if abs(v) > max_value:
                    logger.warning(f"Value {v} exceeded allowed range {max_value}.")

    def wait_for_data(self) -> tuple[IMUData, NDArray]:
        """Block until valid IMU data and pose are available."""
        logger.trace("Waiting for IMU data...")
        imu_data, pose = None, None
        start_time = time.time()
        wait_time = self.imu_config.wait_time_sec
        while imu_data is None or pose is None:
            imu_data, pose = self.__call__()
            dt = time.time() - start_time
            if dt > wait_time:
                msg = f"Waited for IMU data for {wait_time:.2f} sec. Exiting."
                logger.error(msg)
                self.close()
                raise OSError(msg)

        logger.debug(f"IMU data: {imu_data}")
        return imu_data, pose
