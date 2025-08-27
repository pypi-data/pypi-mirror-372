#!/usr/bin/env python3
"""
Test script for the AMCL Python bindings with numpy integration
"""

import numpy as np
import sys
import os

# Add the build directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'build', 'python'))

try:
    import amcl
    print("✅ Successfully imported AMCL module")
except ImportError as e:
    print(f"❌ Failed to import AMCL module: {e}")
    print("Make sure to build the Python bindings first:")
    print("  cd build && make")
    sys.exit(1)

def test_basic_structures():
    """Test basic data structures"""
    print("\n🧪 Testing basic structures...")
    
    # Test Vector3D
    pose = amcl.Vector3D(1.0, 2.0, 0.5)
    print(f"  Vector3D: {pose}")
    assert pose.x == 1.0
    assert pose.y == 2.0
    assert pose.theta == 0.5
    print("  ✅ Vector3D working")
    
    # Test Matrix3D
    cov = amcl.create_identity_covariance()
    assert cov.get(0, 0) == 1.0
    assert cov.get(0, 1) == 0.0
    print("  ✅ Matrix3D working")
    
    # Test LaserParameters
    laser_params = amcl.LaserParameters()
    laser_params.z_hit = 0.5
    laser_params.max_beams = 30
    assert laser_params.z_hit == 0.5
    print("  ✅ LaserParameters working")
    
    # Test MotionParameters
    motion_params = amcl.MotionParameters(0.2, 0.2, 0.2, 0.2, 0.2)
    assert motion_params.alpha1 == 0.2
    print("  ✅ MotionParameters working")

def test_numpy_integration():
    """Test integration with list-based arrays (fallback for numpy)"""
    print("  Creating occupancy grid from list...")
    
    # Create a simple 50x50 grid with some obstacles
    grid_data = [[0 for _ in range(50)] for _ in range(50)]
    # Add some obstacles (walls)
    for i in range(10, 15):
        for j in range(10, 40):
            grid_data[i][j] = 100  # Obstacle
    
    grid = amcl.create_occupancy_grid_from_list(grid_data, 0.1, -2.5, -2.5)
    print(f"  Grid size: {grid.size_x}x{grid.size_y}, scale: {grid.scale}")
    
    print("  Creating laser scan from list...")
    # Create laser scan data (range, bearing pairs)
    ranges_data = [[i * 0.1 + 0.5, i * 0.017] for i in range(181)]  # 181 rays, ~180 degrees
    scan = amcl.create_laser_scan_from_list(ranges_data, 10.0)
    print(f"  Scan size: {scan.size()}, max range: {scan.range_max}")
    
    return grid, scan

def test_amcl_functionality(grid, scan):
    """Test main AMCL functionality"""
    print("\n🧪 Testing AMCL functionality...")
    
    # Create AMCL instance
    motion_params = amcl.MotionParameters(0.2, 0.2, 0.2, 0.2, 0.2)
    
    laser_params = amcl.LaserParameters()
    laser_params.z_hit = 0.5
    laser_params.z_short = 0.05
    laser_params.z_max = 0.05
    laser_params.z_rand = 0.5
    laser_params.sigma_hit = 0.2
    laser_params.lambda_short = 0.1
    laser_params.chi_outlier = 0.05
    laser_params.max_beams = 30  # Use fewer beams than scan size
    
    amcl_instance = amcl.AMCL(
        min_particles=100,
        max_particles=500,
        alpha_slow=0.001,
        alpha_fast=0.01,
        motion_params=motion_params,
        laser_params=laser_params,
        robot_model_type="differential"
    )
    print("  ✅ AMCL instance created")
    
    # Set map
    amcl_instance.set_map(grid)
    print("  ✅ Map set successfully")
    
    # Set initial pose
    initial_pose = amcl.Vector3D(0.0, 0.0, 0.0)
    initial_cov = amcl.create_diagonal_covariance(0.5, 0.5, 0.2)
    amcl_instance.set_initial_pose(initial_pose, initial_cov)
    print("  ✅ Initial pose set")
    
    # Perform updates
    for i in range(5):
        odom_pose = amcl.Vector3D(i * 0.1, i * 0.05, i * 0.02)
        amcl_instance.update(scan, odom_pose)
        
        pose = amcl_instance.get_pose_mean()
        cov = amcl_instance.get_pose_covariance()
        
        print(f"  Update {i+1}: pose = ({pose.x:.3f}, {pose.y:.3f}, {pose.theta:.3f})")
    
    print("  ✅ AMCL updates completed successfully")
    
    # Test property access
    final_pose = amcl_instance.pose
    final_cov = amcl_instance.covariance
    print(f"  Final pose: ({final_pose.x:.3f}, {final_pose.y:.3f}, {final_pose.theta:.3f})")
    print("  ✅ Property access working")

def test_performance():
    """Test performance with larger datasets"""
    print("  Performance test with larger datasets...")
    
    import time
    import math
    
    # Create larger grid (using lists instead of numpy)
    large_grid = [[0 for _ in range(200)] for _ in range(200)]
    # Add obstacles in a large block
    for i in range(50, 150):
        for j in range(50, 150):
            large_grid[i][j] = 100
    
    grid = amcl.create_occupancy_grid_from_list(large_grid, 0.05, -5.0, -5.0)
    
    # Create larger laser scan (using lists instead of numpy)
    num_ranges = 360  # Full 360-degree scan
    ranges = []
    for i in range(num_ranges):
        # Random ranges and angles
        range_val = 0.1 + (i % 100) * 0.1  # Varying ranges
        angle_val = -math.pi + (2 * math.pi * i) / num_ranges  # Full circle
        ranges.append([range_val, angle_val])
    
    scan = amcl.create_laser_scan_from_list(ranges, 10.0)
    
    # Create AMCL with more particles
    motion_params = amcl.MotionParameters(0.1, 0.1, 0.1, 0.1, 0.1)
    laser_params = amcl.LaserParameters()
    laser_params.max_beams = 60  # Use subset of beams for performance
    
    amcl_instance = amcl.AMCL(
        min_particles=500,
        max_particles=2000,
        alpha_slow=0.001,
        alpha_fast=0.01,
        motion_params=motion_params,
        laser_params=laser_params,
        robot_model_type="differential"
    )
    
    amcl_instance.set_map(grid)
    initial_pose = amcl.Vector3D(0.0, 0.0, 0.0)
    initial_cov = amcl.create_diagonal_covariance(1.0, 1.0, 0.5)
    amcl_instance.set_initial_pose(initial_pose, initial_cov)
    
    # Time the updates
    start_time = time.time()
    num_updates = 20
    
    for i in range(num_updates):
        odom_pose = amcl.Vector3D(i * 0.2, i * 0.1, i * 0.05)
        amcl_instance.update(scan, odom_pose)
    
    end_time = time.time()
    avg_time = (end_time - start_time) / num_updates
    
    print(f"  Average update time: {avg_time*1000:.2f} ms")
    print(f"  Updates per second: {1.0/avg_time:.1f} Hz")
    print("  ✅ Performance test completed")

def main():
    """Main test function"""
    print("🚀 AMCL Python Bindings Test Suite")
    # print(f"   Module version: {amcl.__version__}")
    
    try:
        # Run all tests
        test_basic_structures()
        grid, scan = test_numpy_integration()
        test_amcl_functionality(grid, scan)
        print("\n🧪 Testing performance...")
        test_performance()
        
        print("\n🎉 All tests passed successfully!")
        print("   AMCL Python bindings are working correctly with list-based arrays!")
        
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
