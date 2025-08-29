"""Point cloud generation utilities."""

from dataclasses import dataclass

import numpy as np
from loguru import logger
from sklearn.neighbors import NearestNeighbors
from tqdm import tqdm


@dataclass
class PointCloudData:
    """Class for storing point cloud data."""

    points: np.ndarray  # Shape: (N, 3)
    colors: np.ndarray  # Shape: (N, 3)

    def filter_by_distance(self, max_distance: float) -> None:
        """Return a subset of points and colors within the specified distance."""
        distances = np.linalg.norm(self.points, axis=1)
        mask = distances < max_distance
        self.points = self.points[mask]
        self.colors = self.colors[mask]

    def down_sample(self, stride: int) -> None:
        """Downsample the point cloud using a stride."""
        self.points = self.points[::stride]
        self.colors = self.colors[::stride]

    def rotate(self, rotation_matrix: np.ndarray) -> None:
        """Rotate the point cloud using a rotation matrix."""
        logger.debug(f"Rotating point cloud by:\n{rotation_matrix}")
        with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
            points_tran = rotation_matrix @ self.points.T
        self.points = points_tran.T

    def estimate_normals(self, k: int) -> np.ndarray:
        """Estimate surface normals from point cloud."""
        neighbors = NearestNeighbors(n_neighbors=k + 1, algorithm="kd_tree").fit(
            self.points
        )
        _, indices = neighbors.kneighbors(self.points)

        normals = np.zeros_like(self.points)

        for i, neighbors in tqdm(
            enumerate(indices),
            total=len(self.points),
            desc="Estimating Normals",
            leave=False,
        ):
            neighbor_pts = self.points[neighbors[1:]]
            centroid = neighbor_pts.mean(axis=0)
            centered = neighbor_pts - centroid
            cov = centered.T @ centered
            _, _, vh = np.linalg.svd(cov)
            normal = vh[-1]
            normal /= np.linalg.norm(normal)

            # Flip normals to face toward the sensor
            to_sensor = -self.points[i]
            if np.dot(normal, to_sensor) < 0:
                normal *= -1

            normals[i] = normal

        return normals


class PointCloudGenerator:
    """Class for generating point clouds from inverse depth maps and images."""

    @staticmethod
    def from_depth_map(
        depth_map: np.ndarray, image: np.ndarray, focal_length_px: float
    ) -> PointCloudData:
        """Generate point cloud from the inverse depth map and image."""
        logger.debug("Creating point cloud from depth map.")
        height_px, width_px = depth_map.shape
        u, v = np.meshgrid(np.arange(width_px), np.arange(height_px))

        center_x, center_y = width_px / 2, height_px / 2
        x = (u - center_x) * depth_map / focal_length_px
        y = (v - center_y) * depth_map / focal_length_px
        z = depth_map

        points_3d = np.stack((x, y, z), axis=-1).reshape(-1, 3)
        colors_rgb = image.reshape(-1, 3)
        valid = z.reshape(-1) > 0

        return PointCloudData(points=points_3d[valid], colors=colors_rgb[valid])


@dataclass
class SceneData:
    """Class for storing scene data."""

    image: np.ndarray
    point_cloud: PointCloudData
    normals: np.ndarray
    depth_map: np.ndarray
    focal_length_px: float
