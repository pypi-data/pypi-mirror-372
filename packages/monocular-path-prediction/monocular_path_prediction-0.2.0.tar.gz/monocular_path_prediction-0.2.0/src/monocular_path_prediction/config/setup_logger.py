"""Configure the logger."""

import sys
from pathlib import Path

from loguru import logger

from monocular_path_prediction.config.definitions import (
    DEFAULT_LOG_LEVEL,
    ENCODING,
    RECORDINGS_DIR,
)
from monocular_path_prediction.utils import get_timestamped_filepath


def setup_logger(
    filename: str,
    stderr_level: str = DEFAULT_LOG_LEVEL,
    log_level: str = DEFAULT_LOG_LEVEL,
    log_dir: Path | None = None,
) -> Path:
    """Configure the logger."""
    logger.remove()

    if log_dir is None:
        log_filepath = RECORDINGS_DIR
    else:
        log_filepath = log_dir
    filepath_with_time = get_timestamped_filepath(
        output_dir=log_filepath, prefix=filename, suffix="log"
    )
    logger.add(sys.stderr, level=stderr_level)
    logger.add(filepath_with_time, level=log_level, encoding=ENCODING, enqueue=True)
    return filepath_with_time
