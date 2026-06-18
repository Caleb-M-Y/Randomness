"""
Camera Calibration Basics (From Python Basics -> Vision Algorithms)
==================================================================
This file shows how simple coding basics become real CV algorithms.

You will see:
1) Camera coordinate systems (world, camera, image)
2) Intrinsics matrix K (focal lengths + principal point)
3) Extrinsics (rotation R + translation t)
4) Projection from 3D world points to 2D image points
5) Planar homography estimation with least squares (DLT + SVD)
6) Pose recovery from homography when K is known
7) Reprojection error as a quality metric

This script is intentionally educational and heavily commented.
It uses synthetic data so you can run it anywhere without real images.

Run:
    python camera_calibration_basics.py
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np


# -----------------------------
# Section 1: Basic Math Utilities
# -----------------------------
# These utility functions are just regular Python functions.
# Algorithms are built by combining many small, testable steps.


def to_homogeneous(points_2d: np.ndarray) -> np.ndarray:
    """Convert Nx2 points to Nx3 homogeneous points by appending 1.

    Homogeneous coordinates make many projective operations linear.
    Example: (x, y) becomes (x, y, 1).
    """
    ones = np.ones((points_2d.shape[0], 1), dtype=float)
    return np.hstack([points_2d, ones])


def from_homogeneous(points_h: np.ndarray) -> np.ndarray:
    """Convert Nx3 homogeneous points back to Nx2 by dividing by w.

    If p = (x, y, w), Euclidean point is (x/w, y/w).
    """
    w = points_h[:, 2:3]
    return points_h[:, :2] / w


# -----------------------------
# Section 2: Camera Model
# -----------------------------
# Pinhole camera equation:
#   x_image_h ~ K [R | t] X_world_h
# where:
# - X_world_h is homogeneous 3D point (X, Y, Z, 1)
# - [R | t] transforms world coordinates -> camera coordinates
# - K transforms normalized camera coords -> pixel coords


def make_intrinsics(fx: float, fy: float, cx: float, cy: float) -> np.ndarray:
    """Create a 3x3 camera intrinsics matrix K.

    K = [[fx,  0, cx],
         [ 0, fy, cy],
         [ 0,  0,  1]]
    """
    return np.array(
        [
            [fx, 0.0, cx],
            [0.0, fy, cy],
            [0.0, 0.0, 1.0],
        ],
        dtype=float,
    )


def rotation_matrix_from_euler(rx_deg: float, ry_deg: float, rz_deg: float) -> np.ndarray:
    """Create a rotation matrix from XYZ Euler angles (degrees).

    This is just matrix multiplication of three basic rotations.
    """
    rx = math.radians(rx_deg)
    ry = math.radians(ry_deg)
    rz = math.radians(rz_deg)

    rx_m = np.array(
        [[1, 0, 0], [0, math.cos(rx), -math.sin(rx)], [0, math.sin(rx), math.cos(rx)]],
        dtype=float,
    )
    ry_m = np.array(
        [[math.cos(ry), 0, math.sin(ry)], [0, 1, 0], [-math.sin(ry), 0, math.cos(ry)]],
        dtype=float,
    )
    rz_m = np.array(
        [[math.cos(rz), -math.sin(rz), 0], [math.sin(rz), math.cos(rz), 0], [0, 0, 1]],
        dtype=float,
    )

    # Order matters in matrix multiplication.
    return rz_m @ ry_m @ rx_m


@dataclass
class CameraPose:
    """Camera extrinsics represented as rotation + translation."""

    rotation: np.ndarray  # 3x3
    translation: np.ndarray  # 3-vector


def world_to_camera(world_points: np.ndarray, pose: CameraPose) -> np.ndarray:
    """Transform Nx3 world points into camera coordinates.

    X_cam = R * X_world + t
    """
    return (pose.rotation @ world_points.T).T + pose.translation.reshape(1, 3)


def project_points(world_points: np.ndarray, k: np.ndarray, pose: CameraPose) -> np.ndarray:
    """Project Nx3 world points into Nx2 image points.

    Steps:
    1) World -> Camera coordinates
    2) Perspective divide: (x/z, y/z)
    3) Intrinsics K to get pixels
    """
    cam_points = world_to_camera(world_points, pose)

    # Keep only points in front of camera (z > 0) in real systems.
    z = cam_points[:, 2:3]
    normalized = cam_points[:, :2] / z

    normalized_h = to_homogeneous(normalized)  # (x/z, y/z, 1)
    image_h = (k @ normalized_h.T).T
    return from_homogeneous(image_h)


# -----------------------------
# Section 3: Generate Synthetic Calibration Board
# -----------------------------
# A checkerboard is common for calibration.
# We create a planar board on Z=0 in world coordinates.


def create_checkerboard_points(rows: int, cols: int, square_size: float) -> np.ndarray:
    """Create Nx3 checkerboard corner coordinates on the plane Z=0.

    square_size is in any consistent unit (meters, millimeters, etc.).
    """
    points = []
    for r in range(rows):
        for c in range(cols):
            x = c * square_size
            y = r * square_size
            z = 0.0
            points.append([x, y, z])
    return np.array(points, dtype=float)


# -----------------------------
# Section 4: Homography Estimation (Planar Mapping)
# -----------------------------
# For planar points (Z=0), mapping from board plane to image is a homography H.
# In homogeneous coordinates:
#   s * [u, v, 1]^T = H * [X, Y, 1]^T
# H has 8 DoF (9 entries up to scale).


def estimate_homography_dlt(plane_points_xy: np.ndarray, image_points_uv: np.ndarray) -> np.ndarray:
    """Estimate homography with Direct Linear Transform (DLT).

    Inputs:
    - plane_points_xy: Nx2 board points (X, Y)
    - image_points_uv: Nx2 image points (u, v)

    Output:
    - H: 3x3 homography matrix (scaled so H[2,2] = 1 when possible)
    """
    if plane_points_xy.shape[0] < 4:
        raise ValueError("Need at least 4 point pairs for homography")

    a_rows = []
    for (x, y), (u, v) in zip(plane_points_xy, image_points_uv):
        # Each correspondence adds two linear equations in h.
        # We solve Ah = 0 using SVD.
        a_rows.append([-x, -y, -1, 0, 0, 0, u * x, u * y, u])
        a_rows.append([0, 0, 0, -x, -y, -1, v * x, v * y, v])

    a = np.array(a_rows, dtype=float)

    # SVD gives the least-squares solution as the singular vector
    # corresponding to the smallest singular value.
    _, _, vt = np.linalg.svd(a)
    h = vt[-1, :]
    h_mat = h.reshape(3, 3)

    # Normalize scale for readability.
    if abs(h_mat[2, 2]) > 1e-12:
        h_mat = h_mat / h_mat[2, 2]

    return h_mat


def project_plane_points_with_homography(plane_points_xy: np.ndarray, h: np.ndarray) -> np.ndarray:
    """Apply homography H to Nx2 plane points and return Nx2 image points."""
    plane_h = to_homogeneous(plane_points_xy)
    img_h = (h @ plane_h.T).T
    return from_homogeneous(img_h)


# -----------------------------
# Section 5: Recover Pose from Homography (K known)
# -----------------------------
# If K is known, we can extract R and t from homography for a planar board.
# Relationship:
#   H ~ K [r1 r2 t]
# Steps:
# 1) B = K^-1 H
# 2) scale lambda so ||r1|| ~= ||r2|| ~= 1
# 3) r3 = r1 x r2
# 4) Orthonormalize rotation with SVD


def pose_from_homography(h: np.ndarray, k: np.ndarray) -> CameraPose:
    """Estimate camera pose from homography and known intrinsics."""
    k_inv = np.linalg.inv(k)
    b = k_inv @ h

    b1 = b[:, 0]
    b2 = b[:, 1]
    b3 = b[:, 2]

    # Scale chosen so rotation columns have unit norm on average.
    scale = 2.0 / (np.linalg.norm(b1) + np.linalg.norm(b2))

    r1 = scale * b1
    r2 = scale * b2
    t = scale * b3
    r3 = np.cross(r1, r2)

    r_approx = np.column_stack([r1, r2, r3])

    # Force a proper rotation matrix (orthonormal, det = +1).
    u, _, vt = np.linalg.svd(r_approx)
    r = u @ vt
    if np.linalg.det(r) < 0:
        r[:, 2] *= -1

    return CameraPose(rotation=r, translation=t)


# -----------------------------
# Section 6: Error Metric
# -----------------------------
# Reprojection error measures calibration quality.
# Smaller is better.


def reprojection_rmse(observed_uv: np.ndarray, predicted_uv: np.ndarray) -> float:
    """Root-mean-square pixel error between observed and predicted points."""
    diff = observed_uv - predicted_uv
    return float(np.sqrt(np.mean(np.sum(diff * diff, axis=1))))


# -----------------------------
# Section 7: End-to-End Demo
# -----------------------------


def main() -> None:
    print("=== Camera Calibration Basics Demo ===")

    # 1) Define camera intrinsics (pretend these are real camera parameters).
    k_true = make_intrinsics(
        fx=900.0,
        fy=880.0,
        cx=640.0,
        cy=360.0,
    )
    print("\nTrue intrinsics K:\n", k_true)

    # 2) Define true camera pose relative to checkerboard.
    r_true = rotation_matrix_from_euler(rx_deg=12.0, ry_deg=-8.0, rz_deg=20.0)
    t_true = np.array([0.05, -0.03, 0.75], dtype=float)
    pose_true = CameraPose(rotation=r_true, translation=t_true)

    # 3) Generate checkerboard world points.
    board_points_3d = create_checkerboard_points(rows=6, cols=8, square_size=0.03)

    # 4) Project 3D points to ideal image points.
    image_points_ideal = project_points(board_points_3d, k_true, pose_true)

    # 5) Add synthetic pixel noise to simulate real measurements.
    rng = np.random.default_rng(seed=42)
    noise = rng.normal(loc=0.0, scale=0.6, size=image_points_ideal.shape)
    image_points_noisy = image_points_ideal + noise

    # 6) Estimate planar homography from board plane points to image points.
    plane_points_xy = board_points_3d[:, :2]
    h_est = estimate_homography_dlt(plane_points_xy, image_points_noisy)
    print("\nEstimated homography H:\n", h_est)

    # 7) Recover camera pose from H and known K.
    pose_est = pose_from_homography(h_est, k_true)

    # 8) Reproject with estimated pose and compare to noisy observations.
    reprojected = project_points(board_points_3d, k_true, pose_est)
    rmse = reprojection_rmse(image_points_noisy, reprojected)

    print("\nTrue translation:", pose_true.translation)
    print("Estimated translation:", pose_est.translation)
    print("\nTrue rotation:\n", pose_true.rotation)
    print("\nEstimated rotation:\n", pose_est.rotation)
    print(f"\nReprojection RMSE: {rmse:.3f} pixels")

    # 9) Show a few point-level comparisons.
    print("\nSample correspondence check (observed vs reprojected):")
    for i in range(5):
        obs = image_points_noisy[i]
        pred = reprojected[i]
        print(f"  pt{i:02d} observed={obs} predicted={pred}")

    # Final takeaway text.
    print("\nTakeaway:")
    print("Algorithms are many small basics combined:")
    print("- loops to build equations")
    print("- arrays/matrices for geometry")
    print("- linear algebra (SVD) for solving")
    print("- functions to keep steps modular")
    print("- error metrics to evaluate results")


if __name__ == "__main__":
    main()
