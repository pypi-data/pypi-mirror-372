"""Definitions for the package."""

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

np.set_printoptions(precision=3, floatmode="fixed", suppress=True)

GRAVITY = 9.80665  # meters / sec^2

# --- Directories ---
ROOT_DIR: Path = Path("src").parent
DATA_DIR: Path = ROOT_DIR / "data"

# Default encoding
ENCODING = "utf-8"
RECORDINGS_DIR: Path = ROOT_DIR / "recordings"
DATE_FORMAT = "%Y-%m-%d_%H-%M-%S"

SERIAL_DEVICE_PREFIX = "/dev/tty.usbmodem"
ports = ["4F21AFA553C21", "CCD82AF127441"]
DEFAULT_SERIAL_PORT = SERIAL_DEVICE_PREFIX + ports[0]

# Default plot settings
FIG_SIZE = (10, 8)  # inches

SPACE_KEY = 32
ESCAPE_KEY = 27

DEFAULT_IMAGE_WIDTH = 640

EPSILON = 1e-6

DISPLAY_ALPHA = 0.6


@dataclass
class LogLevel:
    """Log level."""

    debug: str = "DEBUG"
    info: str = "INFO"
    warning: str = "WARNING"
    error: str = "ERROR"
    critical: str = "CRITICAL"


DEFAULT_LOG_LEVEL = LogLevel.info


@dataclass
class Colors:
    """Color constants."""

    red: tuple[int, int, int] = (0, 0, 255)
    green: tuple[int, int, int] = (0, 255, 0)
    blue: tuple[int, int, int] = (255, 0, 0)
    yellow: tuple[int, int, int] = (0, 255, 255)
    white: tuple[int, int, int] = (255, 255, 255)
    black: tuple[int, int, int] = (0, 0, 0)
    gray: tuple[int, int, int] = (128, 128, 128)


# settings for the Depth Anything V2 models
PRETRAINED_MODEL_DIR = DATA_DIR / "checkpoints"
MODEL_EXTENSION = ".pth"


@dataclass
class ModelSize:
    """Define the depth estimation model sizes."""

    small = "vits"
    medium = "vitb"
    large = "vitl"


MODEL_CONFIGS = {
    ModelSize.small: {
        "encoder": "vits",
        "features": 64,
        "out_channels": [48, 96, 192, 384],
    },
    ModelSize.medium: {
        "encoder": "vitb",
        "features": 128,
        "out_channels": [96, 192, 384, 768],
    },
    ModelSize.large: {
        "encoder": "vitl",
        "features": 256,
        "out_channels": [256, 512, 1024, 1024],
    },
}


# IMU settings
@dataclass
class ImuConfig:
    """Class for configuring the IMU."""

    time_pattern = r"Time:\s*([0-9.]+)"
    meas_pattern = r"Measurements:\s*(\[.*\])"
    delta_time_sec: float = 0.01
    madgwick_filter_gain: float = 0.033
    gyro_range_rps: float = np.deg2rad(1000.0)  # rad / sec
    accel_range_gs: float = 8.0 * GRAVITY  # meters / sec ^2
    wait_time_sec: float = 5.0


@dataclass
class SerialConfig:
    """Class for configuring a serial device."""

    port: str = DEFAULT_SERIAL_PORT
    baud_rate: int = 115200
    timeout: float = 0.1
    encoder: str = ENCODING
    loop_delay: float = 0.001


@dataclass
class PipelineConfig:
    """Configuration for the pipeline."""

    model_size: str = ModelSize.small
    camera_index: int | None = 0
    imu_config: SerialConfig = field(default_factory=SerialConfig)
    max_point_distance: float = 1.0
    output_dir: Path = RECORDINGS_DIR
    show_results: bool = False
    log_level: str = DEFAULT_LOG_LEVEL


@dataclass
class CameraCalibrationConfig:
    """Hold calibration parameters and runtime options.

    Configure the chessboard target, capture behavior, and I/O paths.

    :param tuple[int, int] checkerboard: (cols, rows) of inner corners.
    :param float square_size_meters: Size of a square in meters (or chosen unit).
    :param int capture_count: Number of valid frames to capture.
    :param Path save_dir: Directory to save captured frames.
    """

    checkerboard: tuple[int, int] = (6, 9)
    square_size_meters: float = 0.020
    capture_count: int = 15
    save_dir: Path = DATA_DIR / "calibration"
    capture_count_min: int = 5
