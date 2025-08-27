#!/usr/bin/env python3
"""
AMCL NumPy Integration Wrapper

This module provides helper functions to seamlessly integrate the AMCL library
with NumPy arrays, converting between numpy arrays and the list-based API.
"""

import amcl

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


def create_occupancy_grid_from_numpy(grid_data, scale, origin_x, origin_y):
    """
    Create an AMCL OccupancyGrid from a NumPy array.
    
    Args:
        grid_data: 2D numpy array (height, width) with int8 values
        scale: Grid resolution (meters per pixel)
        origin_x: X coordinate of the grid origin
        origin_y: Y coordinate of the grid origin
        
    Returns:
        AMCL OccupancyGrid object
    """
    if not HAS_NUMPY:
        raise ImportError("NumPy is not available")
    
    if not isinstance(grid_data, np.ndarray):
        raise TypeError("grid_data must be a numpy array")
    
    if grid_data.ndim != 2:
        raise ValueError("grid_data must be a 2D array")
    
    # Convert numpy array to nested list
    grid_list = grid_data.tolist()
    
    return amcl.create_occupancy_grid_from_list(grid_list, scale, origin_x, origin_y)


def create_laser_scan_from_numpy(ranges_data, range_max):
    """
    Create an AMCL LaserScan from a NumPy array.
    
    Args:
        ranges_data: 2D numpy array (N, 2) where each row is [range, bearing]
        range_max: Maximum range of the laser scanner
        
    Returns:
        AMCL LaserScan object
    """
    if not HAS_NUMPY:
        raise ImportError("NumPy is not available")
    
    if not isinstance(ranges_data, np.ndarray):
        raise TypeError("ranges_data must be a numpy array")
    
    if ranges_data.ndim != 2 or ranges_data.shape[1] != 2:
        raise ValueError("ranges_data must be a 2D array with shape (N, 2)")
    
    # Convert numpy array to list of lists
    ranges_list = ranges_data.tolist()
    
    return amcl.create_laser_scan_from_list(ranges_list, range_max)


def occupancy_grid_to_numpy(grid):
    """
    Convert an AMCL OccupancyGrid to a NumPy array.
    
    Args:
        grid: AMCL OccupancyGrid object
        
    Returns:
        2D numpy array (height, width) with int8 values
    """
    if not HAS_NUMPY:
        raise ImportError("NumPy is not available")
    
    # Get grid data as nested list
    grid_list = grid.to_list()
    
    # Convert to numpy array
    return np.array(grid_list, dtype=np.int8)


def laser_scan_to_numpy(scan):
    """
    Convert an AMCL LaserScan to a NumPy array.
    
    Args:
        scan: AMCL LaserScan object
        
    Returns:
        2D numpy array (N, 2) where each row is [range, bearing]
    """
    if not HAS_NUMPY:
        raise ImportError("NumPy is not available")
    
    # Convert ranges list to numpy array
    return np.array(scan.ranges, dtype=np.float64)


# Example usage and demo functions
def demo_numpy_integration():
    """Demonstrate AMCL with NumPy arrays."""
    if not HAS_NUMPY:
        print("NumPy not available. Install with: pip install numpy")
        return
    
    print("🚀 AMCL NumPy Integration Demo")
    print("=" * 40)
    
    # Create occupancy grid using NumPy
    print("1. Creating occupancy grid with NumPy...")
    grid_data = np.zeros((100, 100), dtype=np.int8)
    grid_data[20:30, 20:80] = 100  # Add obstacle
    grid_data[70:80, 20:80] = 100  # Add another obstacle
    
    grid = create_occupancy_grid_from_numpy(grid_data, 0.1, -5.0, -5.0)
    print(f"   Grid size: {grid.size_x}x{grid.size_y}")
    
    # Create laser scan using NumPy
    print("2. Creating laser scan with NumPy...")
    num_rays = 180
    angles = np.linspace(-np.pi/2, np.pi/2, num_rays)
    ranges = np.random.uniform(0.5, 8.0, num_rays)
    laser_data = np.column_stack([ranges, angles])
    
    scan = create_laser_scan_from_numpy(laser_data, 10.0)
    print(f"   Scan rays: {scan.size()}")
    
    # Convert back to NumPy arrays
    print("3. Converting back to NumPy...")
    grid_numpy = occupancy_grid_to_numpy(grid)
    scan_numpy = laser_scan_to_numpy(scan)
    print(f"   Grid array shape: {grid_numpy.shape}")
    print(f"   Scan array shape: {scan_numpy.shape}")
    
    # Use with AMCL
    print("4. Running AMCL localization...")
    motion_params = amcl.MotionParameters(0.1, 0.1, 0.1, 0.1, 0.1)
    laser_params = amcl.LaserParameters()
    
    amcl_instance = amcl.AMCL(
        min_particles=100,
        max_particles=500,
        alpha_slow=0.001,
        alpha_fast=0.1,
        motion_params=motion_params,
        laser_params=laser_params,
        robot_model_type="differential"
    )
    
    amcl_instance.set_map(grid)
    
    # Set initial pose
    initial_pose = amcl.Vector3D(0.0, 0.0, 0.0)
    initial_cov = amcl.Matrix3D()
    initial_cov.set(0, 0, 0.25)  # x variance
    initial_cov.set(1, 1, 0.25)  # y variance
    initial_cov.set(2, 2, 0.06)  # theta variance
    amcl_instance.set_initial_pose(initial_pose, initial_cov)
    
    # Simulate some updates
    for i in range(20):
        odom_pose = amcl.Vector3D(i * 0.1, 0.0, 0.0)
        amcl_instance.update(scan, odom_pose)
        pose = amcl_instance.get_pose_mean()
        print(f"   Update {i+1}: pose = ({pose.x:.3f}, {pose.y:.3f}, {pose.theta:.3f})")
    
    print("\n✅ NumPy integration demo completed!")


if __name__ == "__main__":
    demo_numpy_integration()
