"""Displayer to show camera frames."""

import cv2
import numpy as np
from loguru import logger
from numpy.typing import NDArray

from monocular_path_prediction.config.definitions import DISPLAY_ALPHA, EPSILON, Colors
from monocular_path_prediction.data.point_cloud import PointCloudData
from monocular_path_prediction.utils import LoopTimer


class Display:
    """Display camera frames."""

    def __init__(self, window_name: str = "Camera Display") -> None:
        super().__init__()
        self.timer: LoopTimer = LoopTimer()
        self.window_name: str = window_name
        self.frame: NDArray | None = None

    def add_frame(self, frame: NDArray) -> None:
        """Add a frame to the display."""
        self.frame = frame.copy()

    def show(self) -> None:
        """Show the frame."""
        cv2.imshow(self.window_name, self.frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            cv2.destroyWindow(self.window_name)

    def add_delta_time(self) -> None:
        """Add delta time to the frame."""
        if self.frame is None:
            return
        delta_time = self.timer.delta_time_sec()
        if delta_time is None:
            text = "Frame rate: N/A fps"
        else:
            text = f"Frame rate: {1 / delta_time:.1f} fps"
        font = cv2.FONT_HERSHEY_SIMPLEX
        location = (10, 30)
        cv2.putText(self.frame, text, location, font, fontScale=0.7, color=Colors.red)
        return

    def add_pose(self, pose: NDArray | None) -> None:
        """Add pose to the frame."""
        if self.frame is None:
            return
        if pose is None:
            logger.debug("No pose specified. Skipping frame.")
            return
        if pose.shape != (3, 3):
            logger.warning(f"Pose has invalid shape {pose.shape}; expected (3, 3).")
            return

        length_pixels = 75
        axes = pose * float(length_pixels)

        height_pixels = np.shape(self.frame)[0]
        width_pixels = np.shape(self.frame)[1]
        origin_x = int(width_pixels - length_pixels)
        origin_y = int(height_pixels - length_pixels)
        origin = (origin_x, origin_y)

        # Project the unit axes onto the camera frame
        for idx_xyz, color in enumerate([Colors.red, Colors.green, Colors.blue]):
            ax_x, ax_z = axes[0, idx_xyz], axes[2, idx_xyz]  # Project to the x-z plane
            ax = (int(origin_x - ax_x), int(origin_y - ax_z))
            cv2.line(self.frame, ax, origin, color=color, thickness=2)
        cv2.circle(self.frame, origin, 3, Colors.yellow, -1)

        return

    def add_depth_map(self, depth_map: NDArray, max_distance: float) -> None:
        """Add depth map to the display."""
        if self.frame is None:
            return

        depth_mask = (depth_map > 0.0) & (depth_map < max_distance)

        # Convert base image to BGR for OpenCV display
        img_bgr = cv2.cvtColor(self.frame.copy(), cv2.COLOR_RGB2BGR).copy()

        # Normalize depth on the masked region (avoid NaNs / empty mask)
        masked_vals = depth_map[depth_mask]
        if masked_vals.size > 0:
            d_min = float(np.nanmin(masked_vals))
            d_max = float(np.nanmax(masked_vals))
            if np.isfinite(d_min) and np.isfinite(d_max) and d_max > d_min:
                depth_norm = (depth_map - d_min) / (d_max - d_min)
            else:
                depth_norm = np.zeros_like(depth_map, dtype=np.float32)
        else:
            depth_norm = np.zeros_like(depth_map, dtype=np.float32)

        # Map to 8-bit and apply colormap
        depth_u8 = np.clip(depth_norm * 255.0, 0, 255).astype(np.uint8)
        depth_color_bgr = cv2.applyColorMap(depth_u8, cv2.COLORMAP_TURBO)

        # Alpha blend ONLY where mask is true
        m3 = np.repeat(depth_mask[:, :, None], 3, axis=2)
        self.frame[m3] = (
            DISPLAY_ALPHA * depth_color_bgr[m3] + (1.0 - DISPLAY_ALPHA) * img_bgr[m3]
        ).astype(np.uint8)

    def add_surface_normals(
        self,
        surface_normals: NDArray,
        point_cloud: PointCloudData,
        focal_length_px: float,
        sample_rate: int,
    ) -> None:
        """Add surface normals to the display."""
        if self.frame is None:
            return

        sample = slice(0, len(point_cloud.points), sample_rate)
        pts_sampled = point_cloud.points[sample]
        nrm_sampled = surface_normals[sample]

        vertical_threshold = 0.9
        vertical_mask = np.abs(nrm_sampled[:, 1]) > vertical_threshold
        pts_sampled = pts_sampled[vertical_mask]
        nrm_sampled = nrm_sampled[vertical_mask]

        uv = self.project_point_cloud(
            points=pts_sampled, focal_length_px=focal_length_px
        )

        if uv is None:
            return
        u, v = uv

        normal_end = pts_sampled + nrm_sampled * 0.05
        u2v2 = self.project_point_cloud(
            points=normal_end, focal_length_px=focal_length_px
        )
        if u2v2 is None:
            return
        u2, v2 = u2v2

        du = u2 - u
        dv = v2 - v
        self.draw_quiver_on_image(u=u, v=v, du=du, dv=dv)

    def project_point_cloud(
        self, points: NDArray, focal_length_px
    ) -> tuple[NDArray, NDArray] | None:
        """Project 3D points to 2D image coordinates."""
        if self.frame is None:
            return None
        x, y, z = points[:, 0], points[:, 1], points[:, 2]
        z = np.maximum(z, EPSILON)
        height, width, _ = self.frame.shape
        cx, cy = width / 2, height / 2

        u = (x * focal_length_px / z) + cx
        v = (y * focal_length_px / z) + cy

        return u, v

    def draw_quiver_on_image(
        self,
        u: np.ndarray,
        v: np.ndarray,
        du: np.ndarray,
        dv: np.ndarray,
    ) -> None:
        """Draw quiver arrows on an OpenCV image.

        :param u: X-coordinates (column positions) of arrow bases.
        :param v: Y-coordinates (row positions) of arrow bases.
        :param du: X-components of direction vectors.
        :param dv: Y-components of direction vectors.
        :return: Image with arrows drawn.
        """
        scale = 0.2
        thickness: int = 1
        tip_length: float = 0.2

        for x, y, dx, dy in zip(u, v, du, dv):
            start_point = (int(x), int(y))
            end_point = (round(x + dx * scale), round(y + dy * scale))
            cv2.arrowedLine(
                self.frame,
                start_point,
                end_point,
                color=Colors.green,
                thickness=thickness,
                tipLength=tip_length,
            )
