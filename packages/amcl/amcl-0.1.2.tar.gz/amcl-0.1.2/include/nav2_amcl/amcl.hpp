#ifndef NAV2_AMCL__AMCL_HPP_
#define NAV2_AMCL__AMCL_HPP_

#include <cstdint>
#include <memory>
#include <vector>
#include <array>
#include <string>

namespace nav2_amcl {

// Modern C++ data structures
struct LaserScan {
  std::vector<std::array<double, 2>> ranges;
  double range_max;
  
  LaserScan(int range_count, double max_range) 
    : ranges(range_count), range_max(max_range) {}
};

struct OccupancyGrid {
  int size_x;
  int size_y;
  double scale;
  double origin_x;
  double origin_y;
  std::vector<int8_t> data;
  
  OccupancyGrid(int sx, int sy, double sc, double ox, double oy)
    : size_x(sx), size_y(sy), scale(sc), origin_x(ox), origin_y(oy)
    , data(sx * sy) {}
};

struct Vector3D {
  std::array<double, 3> v;
  
  Vector3D() : v{{0.0, 0.0, 0.0}} {}
  Vector3D(double x, double y, double z) : v{{x, y, z}} {}
};

struct Matrix3D {
  std::array<std::array<double, 3>, 3> m;
  
  Matrix3D() {
    for (auto& row : m) {
      row.fill(0.0);
    }
  }
};

struct LaserParameters {
  double z_hit, z_short, z_max, z_rand, sigma_hit;
  double lambda_short, chi_outlier;
  int max_beams;
  
  LaserParameters() = default;
  
  LaserParameters(double hit, double short_val, double max_val, double rand_val, 
                 double sigma, double lambda, double chi, int beams)
    : z_hit(hit), z_short(short_val), z_max(max_val), z_rand(rand_val)
    , sigma_hit(sigma), lambda_short(lambda), chi_outlier(chi), max_beams(beams) {}
};

struct MotionParameters {
  double alpha1, alpha2, alpha3, alpha4, alpha5;
  
  MotionParameters(double a1, double a2, double a3, double a4, double a5)
    : alpha1(a1), alpha2(a2), alpha3(a3), alpha4(a4), alpha5(a5) {}
};

// Forward declarations for C++ classes
class Laser;
class MotionModel;

class AMCL {
public:
  // Constructor with parameters
  AMCL(int min_particles, int max_particles,
       double alpha_slow, double alpha_fast,
       const MotionParameters& motion_params,
       const LaserParameters& laser_params,
       const std::string& robot_model_type);
  
  // Destructor
  ~AMCL();
  
  // Delete copy constructor and assignment operator for safety
  AMCL(const AMCL&) = delete;
  AMCL& operator=(const AMCL&) = delete;
  
  // Move constructor and assignment operator
  AMCL(AMCL&& other) noexcept;
  AMCL& operator=(AMCL&& other) noexcept;
  
  // Public interface methods
  void setMap(const OccupancyGrid& grid);
  void update(const LaserScan& scan, const Vector3D& odom_pose);
  Vector3D getPoseMean() const;
  Matrix3D getPoseCovariance() const;
  void setInitialPose(const Vector3D& pose, const Matrix3D& cov);
  void setLaserPose(const Vector3D& laser_pose);
  
  // Getters
  bool isInitialized() const;
  
private:
  // Pimpl idiom to hide implementation details
  class Impl;
  std::unique_ptr<Impl> impl_;
};

} // namespace nav2_amcl

#endif  // NAV2_AMCL__AMCL_HPP_