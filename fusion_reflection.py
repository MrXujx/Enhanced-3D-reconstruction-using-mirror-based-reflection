import open3d as o3d
import numpy as np

def read_ply(filepath):
    # Load the point cloud from the PLY file, including colors
    pcd = o3d.io.read_point_cloud(filepath)
    return pcd

def split_and_mirror_point_cloud(pcd, plane_params):
    # Extract plane parameters
    a, b, c, d = plane_params

    # Convert point cloud to numpy array for points and colors
    points = np.asarray(pcd.points)
    colors = np.asarray(pcd.colors)

    # Calculate distances from points to the plane
    distances = (a * points[:, 0] + b * points[:, 1] + c * points[:, 2] + d) / np.sqrt(a**2 + b**2 + c**2)

    # Split point cloud into two parts based on the plane
    above_plane_indices = distances >= 0
    below_plane_indices = distances < 0
    above_plane_points = points[above_plane_indices]
    below_plane_points = points[below_plane_indices]
    above_plane_colors = colors[above_plane_indices]
    below_plane_colors = colors[below_plane_indices]

    # Calculate mirrored points for the points below the plane
    mirror_distances = 2 * distances[below_plane_indices].reshape(-1, 1)
    mirrored_points = below_plane_points - mirror_distances * np.array([a, b, c]) / np.sqrt(a**2 + b**2 + c**2)

    # Create point clouds from numpy arrays
    pcd_A = o3d.geometry.PointCloud()
    pcd_A.points = o3d.utility.Vector3dVector(above_plane_points)
    pcd_A.colors = o3d.utility.Vector3dVector(above_plane_colors)
    pcd_A.paint_uniform_color([0, 0, 1])  # Temporary color for visualization

    pcd_B = o3d.geometry.PointCloud()
    pcd_B.points = o3d.utility.Vector3dVector(mirrored_points)
    pcd_B.colors = o3d.utility.Vector3dVector(below_plane_colors)
    pcd_B.paint_uniform_color([1, 0, 0])  # Temporary color for visualization

    return pcd_A, pcd_B, above_plane_colors, below_plane_colors

def visualize_point_clouds(pcd_A, pcd_B):
    # Create a new point cloud for combined visualization
    pcd_combined = o3d.geometry.PointCloud()
    pcd_combined.points = o3d.utility.Vector3dVector(np.vstack((np.asarray(pcd_A.points), np.asarray(pcd_B.points))))
    pcd_combined.colors = o3d.utility.Vector3dVector(np.vstack((np.asarray(pcd_A.colors), np.asarray(pcd_B.colors))))
    o3d.visualization.draw_geometries([pcd_combined])

def save_point_clouds(pcd_A, pcd_B, filepath_A, filepath_B, o_A_colors, o_B_colors):
    # Restore original colors for saving
    pcd_A.colors = o3d.utility.Vector3dVector(o_A_colors)
    pcd_B.colors = o3d.utility.Vector3dVector(o_B_colors)
    o3d.io.write_point_cloud(filepath_A, pcd_A)
    o3d.io.write_point_cloud(filepath_B, pcd_B)

def calculate_plane(point1, point2, point3):
    # Convert points to numpy arrays
    P1 = np.array(point1)
    P2 = np.array(point2)
    P3 = np.array(point3)

    # Calculate vectors from the points
    v = P2 - P1
    w = P3 - P1

    # Cross product to find the normal vector (A, B, C)
    n = np.cross(v, w)

    # Calculate D using point P1
    D = -np.dot(n, P1)

    # Return the coefficients as individual numbers
    A, B, C = n
    return A, B, C, D

# Usage Example
path = "X://mirror//car//output//"
pcd = read_ply(path + "pointcloud.ply")
A, B, C, D = calculate_plane([1.551208, 0.025813, 12.980596], [-4.784678, -0.348964, 13.797467], [5.716069, 0.599323, 11.983661])
plane_params = [A, B, C, D]
pcd_A, pcd_B, o_A_colors, o_B_colors = split_and_mirror_point_cloud(pcd, plane_params)
visualize_point_clouds(pcd_A, pcd_B)
save_point_clouds(pcd_A, pcd_B, path + "A.ply", path + "B.ply", o_A_colors, o_B_colors)
