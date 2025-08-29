"""Camera tools for the monocular path prediction pipeline."""

import plistlib
import subprocess

import cv2

from monocular_path_prediction.sensors.device import DeviceInfo


def map_cameras_to_indices(max_probe: int = 8) -> list[DeviceInfo]:
    """Map OpenCV indices to macOS camera names (best-effort by order).

    Pairs indices and names by list order; truncates to the shorter list.
    Falls back to generic names if names are unavailable.

    :return: List of CameraInfo entries in display order.
    :rtype: list[CameraInfo]
    """
    names = get_mac_cameras()
    indices = scan_cameras(max(len(names), 1) if names else max_probe)

    n = min(len(indices), len(names))
    if n == 0 and indices:
        return [DeviceInfo(index=i, name=f"Camera {i}") for i in indices]
    return [DeviceInfo(index=indices[i], name=names[i]) for i in range(n)]


def get_mac_cameras() -> list[str]:
    """Get camera names from macOS `system_profiler`.

    :return: List of camera names.
    :rtype: list[str]
    """
    result = subprocess.run(
        ["system_profiler", "SPCameraDataType", "-xml"],
        capture_output=True,
        text=False,
        check=True,
    )
    plist = plistlib.loads(result.stdout)
    names: list[str] = []
    for item in plist:
        for cam in item.get("_items", []):
            name = cam.get("_name")
            if name:
                names.append(name)
    return names


def scan_cameras(max_index: int) -> list[int]:
    """Scan OpenCV camera indices and return those that open.

    :param int max_index: Highest index (exclusive) to probe.
    :return: List of available indices.
    :rtype: List[int]
    """
    found: list[int] = []
    for i in range(max_index):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            found.append(i)
            cap.release()
    return found
