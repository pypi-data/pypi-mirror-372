#include "nav2_amcl/amcl.hpp"
#include <iostream>
#include <cmath>
#include <vector>

int main() {
  std::cout << "Modern C++ AMCL Demonstration" << std::endl;
  
  try {
    // Create motion parameters
    nav2_amcl::MotionParameters motion_params(0.2, 0.2, 0.2, 0.2, 0.2);
    
    // Create laser parameters  
    nav2_amcl::LaserParameters laser_params(0.95, 0.1, 0.05, 0.05, 0.2, 0.5, 0.05, 10);
    
    // Create AMCL instance using modern C++ interface
    nav2_amcl::AMCL amcl(500, 2000, 0.0, 0.0, motion_params, laser_params, "differential");
    
    std::cout << "AMCL instance created successfully." << std::endl;
    
    // Create a modern occupancy grid
    nav2_amcl::OccupancyGrid grid(100, 100, 0.1, 0.0, 0.0);
    
    // Initialize with border obstacles
    for (int i = 0; i < grid.size_y; i++) {
      for (int j = 0; j < grid.size_x; j++) {
        int idx = i * grid.size_x + j;
        if (i == 0 || i == grid.size_y - 1 || j == 0 || j == grid.size_x - 1) {
          grid.data[idx] = 100; // Occupied
        } else {
          grid.data[idx] = 0;   // Free
        }
      }
    }
    
    amcl.setMap(grid);
    std::cout << "Map set with size: " << grid.size_x << "x" << grid.size_y << std::endl;
    
    // Set initial pose
    nav2_amcl::Vector3D initial_pose(5.0, 5.0, 0.0);
    nav2_amcl::Matrix3D initial_cov;
    initial_cov.m[0][0] = 0.25;
    initial_cov.m[1][1] = 0.25;
    initial_cov.m[2][2] = 0.0685;
    
    amcl.setInitialPose(initial_pose, initial_cov);
    std::cout << "Initial pose set." << std::endl;
    
    // Main loop with modern interface
    for (int i = 0; i < 10; i++) {
      // Create laser scan
      nav2_amcl::LaserScan scan(10, 10.0);
      for (int j = 0; j < 10; j++) {
        scan.ranges[j][0] = 5.0; // Range
        scan.ranges[j][1] = j * (2 * M_PI / 10); // Angle
      }
      
      // Odometry pose
      nav2_amcl::Vector3D odom_pose(5.0 + i * 0.1, 5.0, 0.0);
      
      std::cout << "Iteration " << i << ": Updating AMCL..." << std::endl;
      
      // Update AMCL
      amcl.update(scan, odom_pose);
      
      // Get pose estimate
      auto pose_mean = amcl.getPoseMean();
      std::cout << "Estimated pose: (" << pose_mean.v[0] << ", " 
                << pose_mean.v[1] << ", " << pose_mean.v[2] << ")" << std::endl;
    }
    
    std::cout << "Modern C++ AMCL demonstration completed successfully." << std::endl;
    
  } catch (const std::exception& e) {
    std::cerr << "Error: " << e.what() << std::endl;
    return 1;
  }
  
  return 0;
}