"""Camera calibration tools for the monocular path prediction pipeline."""

from typing import Protocol, runtime_checkable

import cv2
import numpy as np
from numpy.typing import NDArray


@runtime_checkable
class PatternDetector(Protocol):
    """Abstract calibration pattern detector."""

    def detect(self, gray: NDArray) -> tuple[bool, NDArray | None]:
        """Detect corners and return (found, corners)."""
        ...

    @property
    def obj_points_template(self) -> NDArray:
        """Return the 3D object points (one board) in calibration units."""
        ...

    @property
    def checkerboard(self) -> tuple[int, int]:
        """Return (cols, rows) of inner corners for drawing/routines."""
        ...


# -----------------------------------------------------------------------------
# Implementations
# -----------------------------------------------------------------------------


class ChessboardDetector(PatternDetector):
    """Detect a standard chessboard (checkerboard) calibration target."""

    def __init__(self, checkerboard: tuple[int, int], square_size: float) -> None:
        self._checkerboard = checkerboard
        self.square_size = square_size

        cols, rows = checkerboard
        objp = np.zeros((cols * rows, 3), np.float32)
        objp[:, :2] = np.mgrid[0:cols, 0:rows].T.reshape(-1, 2)
        objp *= float(square_size)
        self._objp = objp

    @property
    def checkerboard(self) -> tuple[int, int]:
        """Return (cols, rows) of inner corners."""
        return self._checkerboard

    @property
    def obj_points_template(self) -> np.ndarray:
        """Return the 3D object points (one board) in calibration units."""
        return self._objp

    def detect(self, gray: np.ndarray) -> tuple[bool, NDArray | None]:
        """Detect chessboard corners and refine to subpixel accuracy.

        :param np.ndarray gray: Grayscale image.
        :return: (found, corners) where corners are None if not found.
        :rtype: Tuple[bool, np.ndarray | None]
        """
        flags = (
            cv2.CALIB_CB_ADAPTIVE_THRESH
            + cv2.CALIB_CB_FAST_CHECK
            + cv2.CALIB_CB_NORMALIZE_IMAGE
        )
        found, corners = cv2.findChessboardCorners(
            image=gray, patternSize=self.checkerboard, flags=flags
        )

        if not found:
            return False, None

        criteria = (
            cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,
            30,
            0.001,
        )
        corners_subpix = cv2.cornerSubPix(
            gray,
            corners,
            winSize=(11, 11),
            zeroZone=(-1, -1),
            criteria=criteria,
        )
        return True, corners_subpix
