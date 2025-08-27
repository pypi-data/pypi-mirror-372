#include <nanobind/nanobind.h>
#include <nanobind/stl/string.h>
#include <nanobind/stl/vector.h>
#include <nanobind/stl/array.h>
#include "nav2_amcl/amcl.hpp"

namespace nb = nanobind;
using namespace nb::literals;
using namespace nav2_amcl;

NB_MODULE(_amcl_impl, m) {
    m.doc() = "Modern C++ AMCL (Adaptive Monte Carlo Localization) library";

    // LaserScan structure
    nb::class_<LaserScan>(m, "LaserScan", "Laser scan data structure")
        .def(nb::init<int, double>(), "range_count"_a, "range_max"_a,
             "Create a laser scan with specified number of ranges and maximum range")
        .def_rw("ranges", &LaserScan::ranges, "Array of [distance, bearing] pairs")
        .def_rw("range_max", &LaserScan::range_max, "Maximum range of the laser")
        .def("size", [](const LaserScan& self) { return self.ranges.size(); },
             "Get number of laser ranges");

    // OccupancyGrid structure
    nb::class_<OccupancyGrid>(m, "OccupancyGrid", "2D occupancy grid map")
        .def(nb::init<int, int, double, double, double>(),
             "size_x"_a, "size_y"_a, "scale"_a, "origin_x"_a, "origin_y"_a,
             "Create an occupancy grid with specified dimensions and resolution")
        .def_rw("size_x", &OccupancyGrid::size_x, "Width of the grid")
        .def_rw("size_y", &OccupancyGrid::size_y, "Height of the grid")
        .def_rw("scale", &OccupancyGrid::scale, "Resolution (meters per cell)")
        .def_rw("origin_x", &OccupancyGrid::origin_x, "X coordinate of origin")
        .def_rw("origin_y", &OccupancyGrid::origin_y, "Y coordinate of origin")
        .def_rw("data", &OccupancyGrid::data, "Grid data (0=free, 100=occupied, -1=unknown)")
        .def("set_from_list", [](OccupancyGrid& self, const std::vector<std::vector<int>>& grid_data) {
            if (grid_data.empty()) return;
            self.size_y = grid_data.size();
            self.size_x = grid_data[0].size();
            self.data.resize(self.size_x * self.size_y);
            
            for (int i = 0; i < self.size_y; ++i) {
                for (int j = 0; j < self.size_x; ++j) {
                    self.data[i * self.size_x + j] = grid_data[i][j];
                }
            }
        }, "grid_data"_a, "Set grid data from 2D list")
        .def("to_list", [](const OccupancyGrid& self) {
            std::vector<std::vector<int>> result(self.size_y, std::vector<int>(self.size_x));
            for (int i = 0; i < self.size_y; ++i) {
                for (int j = 0; j < self.size_x; ++j) {
                    result[i][j] = self.data[i * self.size_x + j];
                }
            }
            return result;
        }, "Convert grid data to 2D list");

    // Vector3D structure
    nb::class_<Vector3D>(m, "Vector3D", "3D vector for poses")
        .def(nb::init<double, double, double>(), "x"_a = 0.0, "y"_a = 0.0, "theta"_a = 0.0,
             "Create a 3D vector (x, y, theta)")
        .def_rw("v", &Vector3D::v, "Vector components [x, y, theta]")
        .def_prop_rw("x", 
                     [](const Vector3D& self) { return self.v[0]; },
                     [](Vector3D& self, double x) { self.v[0] = x; },
                     "X coordinate")
        .def_prop_rw("y",
                     [](const Vector3D& self) { return self.v[1]; },
                     [](Vector3D& self, double y) { self.v[1] = y; },
                     "Y coordinate")
        .def_prop_rw("theta",
                     [](const Vector3D& self) { return self.v[2]; },
                     [](Vector3D& self, double theta) { self.v[2] = theta; },
                     "Orientation angle")
        .def("__repr__", [](const Vector3D& self) {
            return "Vector3D(x=" + std::to_string(self.v[0]) + 
                   ", y=" + std::to_string(self.v[1]) + 
                   ", theta=" + std::to_string(self.v[2]) + ")";
        });

    // Matrix3D structure
    nb::class_<Matrix3D>(m, "Matrix3D", "3x3 matrix for covariances")
        .def(nb::init<>(), "Create a zero 3x3 matrix")
        .def_rw("m", &Matrix3D::m, "Matrix elements [3][3]")
        .def("set", [](Matrix3D& self, int i, int j, double value) {
            if (i >= 0 && i < 3 && j >= 0 && j < 3) {
                self.m[i][j] = value;
            }
        }, "i"_a, "j"_a, "value"_a, "Set matrix element at (i,j)")
        .def("get", [](const Matrix3D& self, int i, int j) {
            if (i >= 0 && i < 3 && j >= 0 && j < 3) {
                return self.m[i][j];
            }
            return 0.0;
        }, "i"_a, "j"_a, "Get matrix element at (i,j)")
        .def("to_list", [](const Matrix3D& self) {
            std::vector<std::vector<double>> result(3, std::vector<double>(3));
            for (int i = 0; i < 3; ++i) {
                for (int j = 0; j < 3; ++j) {
                    result[i][j] = self.m[i][j];
                }
            }
            return result;
        }, "Convert to 2D list")
        .def("from_list", [](Matrix3D& self, const std::vector<std::vector<double>>& matrix_data) {
            for (int i = 0; i < 3 && i < matrix_data.size(); ++i) {
                for (int j = 0; j < 3 && j < matrix_data[i].size(); ++j) {
                    self.m[i][j] = matrix_data[i][j];
                }
            }
        }, "matrix_data"_a, "Set from 2D list");

    // LaserParameters structure
    nb::class_<LaserParameters>(m, "LaserParameters", "Laser model parameters")
        .def(nb::init<double, double, double, double, double, double, double, int>(),
             "z_hit"_a, "z_short"_a, "z_max"_a, "z_rand"_a,
             "sigma_hit"_a, "lambda_short"_a, "chi_outlier"_a, "max_beams"_a,
             "Create laser parameters")
        .def_rw("z_hit", &LaserParameters::z_hit, "Weight for correct range readings")
        .def_rw("z_short", &LaserParameters::z_short, "Weight for short range readings")
        .def_rw("z_max", &LaserParameters::z_max, "Weight for max range readings")
        .def_rw("z_rand", &LaserParameters::z_rand, "Weight for random readings")
        .def_rw("sigma_hit", &LaserParameters::sigma_hit, "Standard deviation for hit readings")
        .def_rw("lambda_short", &LaserParameters::lambda_short, "Exponential decay parameter for short readings")
        .def_rw("chi_outlier", &LaserParameters::chi_outlier, "Outlier rejection threshold")
        .def_rw("max_beams", &LaserParameters::max_beams, "Maximum number of beams to use");

    // MotionParameters structure
    nb::class_<MotionParameters>(m, "MotionParameters", "Motion model parameters")
        .def(nb::init<double, double, double, double, double>(),
             "alpha1"_a, "alpha2"_a, "alpha3"_a, "alpha4"_a, "alpha5"_a,
             "Create motion parameters")
        .def_rw("alpha1", &MotionParameters::alpha1, "Rotation noise from rotation")
        .def_rw("alpha2", &MotionParameters::alpha2, "Rotation noise from translation")
        .def_rw("alpha3", &MotionParameters::alpha3, "Translation noise from translation")
        .def_rw("alpha4", &MotionParameters::alpha4, "Translation noise from rotation")
        .def_rw("alpha5", &MotionParameters::alpha5, "Translation noise (constant)");

    // Main AMCL class
    nb::class_<AMCL>(m, "AMCL", "Adaptive Monte Carlo Localization")
        .def(nb::init<int, int, double, double, const MotionParameters&, const LaserParameters&, const std::string&>(),
             "min_particles"_a, "max_particles"_a, "alpha_slow"_a, "alpha_fast"_a,
             "motion_params"_a, "laser_params"_a, "robot_model_type"_a,
             "Create AMCL instance\n\n"
             "Parameters:\n"
             "  min_particles: Minimum number of particles\n"
             "  max_particles: Maximum number of particles\n"
             "  alpha_slow: Slow decay rate for adaptive resampling\n"
             "  alpha_fast: Fast decay rate for adaptive resampling\n"
             "  motion_params: Motion model parameters\n"
             "  laser_params: Laser model parameters\n"
             "  robot_model_type: Robot model type ('differential' or 'omni')")
        .def("set_map", &AMCL::setMap, "grid"_a,
             "Set the occupancy grid map")
        .def("update", &AMCL::update, "scan"_a, "odom_pose"_a,
             "Update particle filter with laser scan and odometry\n\n"
             "Parameters:\n"
             "  scan: LaserScan data\n"
             "  odom_pose: Odometry pose as Vector3D")
        .def("get_pose_mean", &AMCL::getPoseMean,
             "Get the mean pose estimate")
        .def("get_pose_covariance", &AMCL::getPoseCovariance,
             "Get the pose covariance matrix")
        .def("set_initial_pose", &AMCL::setInitialPose, "pose"_a, "cov"_a,
             "Set initial pose estimate with covariance")
        .def("set_laser_pose", &AMCL::setLaserPose, "laser_pose"_a,
             "Set laser sensor pose offset relative to robot base frame")
        .def("is_initialized", &AMCL::isInitialized,
             "Check if particle filter is initialized")
        .def_prop_ro("pose", &AMCL::getPoseMean,
                     "Current pose estimate (read-only)")
        .def_prop_ro("covariance", &AMCL::getPoseCovariance,
                     "Current pose covariance (read-only)");

    // Convenience functions for creating objects from Python lists
    m.def("create_laser_scan_from_list", 
          [](const std::vector<std::vector<double>>& ranges_list, double range_max) {
              size_t num_ranges = ranges_list.size();
              LaserScan scan(num_ranges, range_max);
              
              for (size_t i = 0; i < num_ranges && i < ranges_list.size(); ++i) {
                  if (ranges_list[i].size() >= 2) {
                      scan.ranges[i][0] = ranges_list[i][0];  // distance
                      scan.ranges[i][1] = ranges_list[i][1];  // bearing
                  }
              }
              
              return scan;
          },
          "ranges"_a, "range_max"_a,
          "Create LaserScan from list of [distance, bearing] pairs");

    m.def("create_occupancy_grid_from_list",
          [](const std::vector<std::vector<int>>& grid_data,
             double scale, double origin_x = 0.0, double origin_y = 0.0) {
              if (grid_data.empty()) {
                  throw std::invalid_argument("Grid data cannot be empty");
              }
              
              int size_y = grid_data.size();
              int size_x = grid_data[0].size();
              
              OccupancyGrid grid(size_x, size_y, scale, origin_x, origin_y);
              
              for (int i = 0; i < size_y; ++i) {
                  for (int j = 0; j < size_x && j < grid_data[i].size(); ++j) {
                      grid.data[i * size_x + j] = grid_data[i][j];
                  }
              }
              
              return grid;
          },
          "grid"_a, "scale"_a, "origin_x"_a = 0.0, "origin_y"_a = 0.0,
          "Create OccupancyGrid from 2D list");

    m.def("create_identity_covariance", []() {
        Matrix3D cov;
        for (int i = 0; i < 3; ++i) {
            for (int j = 0; j < 3; ++j) {
                cov.m[i][j] = (i == j) ? 1.0 : 0.0;
            }
        }
        return cov;
    }, "Create a 3x3 identity covariance matrix");

    m.def("create_diagonal_covariance", [](double x_var, double y_var, double theta_var) {
        Matrix3D cov;
        for (int i = 0; i < 3; ++i) {
            for (int j = 0; j < 3; ++j) {
                cov.m[i][j] = 0.0;
            }
        }
        cov.m[0][0] = x_var;
        cov.m[1][1] = y_var;
        cov.m[2][2] = theta_var;
        return cov;
    }, "x_var"_a, "y_var"_a, "theta_var"_a,
       "Create a diagonal covariance matrix with specified variances");

    // Module constants
    m.attr("__version__") = "1.0.0";
}
