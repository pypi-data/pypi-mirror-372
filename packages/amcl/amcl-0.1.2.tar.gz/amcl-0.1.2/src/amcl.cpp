#include "nav2_amcl/amcl.hpp"
#include "nav2_amcl/map/map.hpp"
#include "nav2_amcl/pf/pf.hpp"
#include "nav2_amcl/sensors/laser/laser.hpp"
#include "nav2_amcl/motion_model/motion_model.hpp"
#include "nav2_amcl/motion_model/differential_motion_model.hpp"
#include "nav2_amcl/motion_model/omni_motion_model.hpp"

#include <memory>
#include <cstdlib>
#include <cmath>
#include <stdexcept>
#include <random>

namespace nav2_amcl {

// Pimpl class containing all the implementation details
class AMCL::Impl {
public:
    map_t* map;
    pf_t* pf;
    std::unique_ptr<Laser> laser;
    std::unique_ptr<MotionModel> motion_model;
    LaserParameters laser_params;
    pf_vector_t odom_pose;
    bool pf_init;
    std::vector<std::array<double, 2>> ranges_buffer;

    Impl() : map(nullptr), pf(nullptr), pf_init(false) {
        odom_pose.v[0] = odom_pose.v[1] = odom_pose.v[2] = 0.0;
    }

    ~Impl() {
        // Clean up in proper order to avoid double free
        laser.reset();  // Reset unique_ptr first
        motion_model.reset();
        
        // Clear ranges buffer
        ranges_buffer.clear();
        
        if (pf) {
            pf_free(pf);
            pf = nullptr;
        }
        if (map) {
            map_free(map);
            map = nullptr;
        }
    }

    // Static helper function for pose generation
    static pf_vector_t uniformPoseGenerator(void* arg) {
        map_t* map = static_cast<map_t*>(arg);
        double min_x = -(map->size_x * map->scale) / 2.0 + map->origin_x;
        double max_x = (map->size_x * map->scale) / 2.0 + map->origin_x;
        double min_y = -(map->size_y * map->scale) / 2.0 + map->origin_y;
        double max_y = (map->size_y * map->scale) / 2.0 + map->origin_y;

        static thread_local std::random_device rd;
        static thread_local std::mt19937 gen(rd());
        static thread_local std::uniform_real_distribution<double> dist(0.0, 1.0);

        pf_vector_t p;
        while (true) {
            p.v[0] = min_x + dist(gen) * (max_x - min_x);
            p.v[1] = min_y + dist(gen) * (max_y - min_y);
            p.v[2] = dist(gen) * 2 * M_PI - M_PI;
            
            int i = MAP_GXWX(map, p.v[0]);
            int j = MAP_GYWY(map, p.v[1]);
            if (MAP_VALID(map, i, j) && (map->cells[MAP_INDEX(map, i, j)].occ_state == -1)) {
                break;
            }
        }
        return p;
    }

    // Helper function to convert from modern OccupancyGrid to internal map_t
    map_t* convertMap(const OccupancyGrid& grid) {
        map_t* map = map_alloc();
        if (!map) {
            throw std::runtime_error("Failed to allocate map");
        }
        
        map->size_x = grid.size_x;
        map->size_y = grid.size_y;
        map->scale = grid.scale;
        map->origin_x = grid.origin_x + (map->size_x / 2) * map->scale;
        map->origin_y = grid.origin_y + (map->size_y / 2) * map->scale;
        
        // Use malloc as expected by the C library
        map->cells = static_cast<map_cell_t*>(malloc(sizeof(map_cell_t) * map->size_x * map->size_y));
        if (!map->cells) {
            map_free(map);
            throw std::runtime_error("Failed to allocate map cells");
        }

        const size_t total_cells = grid.data.size();
        for (size_t i = 0; i < total_cells; i++) {
            if (grid.data[i] == 0) {
                map->cells[i].occ_state = -1;  // Free
            } else if (grid.data[i] == 100) {
                map->cells[i].occ_state = +1;  // Occupied
            } else {
                map->cells[i].occ_state = 0;   // Unknown
            }
        }

        return map;
    }
};

// Constructor
AMCL::AMCL(int min_particles, int max_particles,
           double alpha_slow, double alpha_fast,
           const MotionParameters& motion_params,
           const LaserParameters& laser_params,
           const std::string& robot_model_type)
    : impl_(std::make_unique<Impl>()) {
    
    try {
        impl_->laser_params = laser_params;
        
        // Initialize particle filter with proper cleanup
        impl_->pf = pf_alloc(min_particles, max_particles, alpha_slow, alpha_fast, Impl::uniformPoseGenerator);
        if (!impl_->pf) {
            throw std::runtime_error("Failed to allocate particle filter");
        }

        // Initialize motion model
        if (robot_model_type == "differential") {
            impl_->motion_model = std::make_unique<DifferentialMotionModel>();
        } else if (robot_model_type == "omni") {
            impl_->motion_model = std::make_unique<OmniMotionModel>();
        } else {
            throw std::invalid_argument("Unknown robot model type: " + robot_model_type);
        }
        
        impl_->motion_model->initialize(motion_params.alpha1, motion_params.alpha2, 
                                      motion_params.alpha3, motion_params.alpha4, 
                                      motion_params.alpha5);

        // Initialize laser model (will be recreated when map is set)
        impl_->laser = std::make_unique<BeamModel>(
            laser_params.z_hit, laser_params.z_short, laser_params.z_max, 
            laser_params.z_rand, laser_params.sigma_hit,
            laser_params.lambda_short, laser_params.chi_outlier, 
            laser_params.max_beams, nullptr);
        
    } catch (const std::exception& e) {
        throw std::runtime_error("AMCL constructor failed: " + std::string(e.what()));
    }
}

// Destructor
AMCL::~AMCL() = default;

// Move constructor
AMCL::AMCL(AMCL&& other) noexcept = default;

// Move assignment operator
AMCL& AMCL::operator=(AMCL&& other) noexcept = default;

void AMCL::setMap(const OccupancyGrid& grid) {
    try {
        if (impl_->map) {
            map_free(impl_->map);
            impl_->map = nullptr;
        }
        impl_->map = impl_->convertMap(grid);
        
        // Recreate laser model with the new map
        impl_->laser = std::make_unique<BeamModel>(
            impl_->laser_params.z_hit, impl_->laser_params.z_short, impl_->laser_params.z_max, 
            impl_->laser_params.z_rand, impl_->laser_params.sigma_hit,
            impl_->laser_params.lambda_short, impl_->laser_params.chi_outlier, 
            impl_->laser_params.max_beams, impl_->map);
            
    } catch (const std::exception& e) {
        throw std::runtime_error("Failed to set map: " + std::string(e.what()));
    }
}

void AMCL::update(const LaserScan& scan, const Vector3D& odom_pose) {
    if (!impl_->map) {
        throw std::runtime_error("Map not set before update");
    }

    pf_vector_t pose;
    pose.v[0] = odom_pose.v[0];
    pose.v[1] = odom_pose.v[1];
    pose.v[2] = odom_pose.v[2];

    if (!impl_->pf_init) {
        impl_->odom_pose = pose;
        impl_->pf_init = true;
    }

    // Compute motion delta
    pf_vector_t delta;
    delta.v[0] = pose.v[0] - impl_->odom_pose.v[0];
    delta.v[1] = pose.v[1] - impl_->odom_pose.v[1];
    delta.v[2] = std::atan2(
        std::sin(pose.v[2] - impl_->odom_pose.v[2]),
        std::cos(pose.v[2] - impl_->odom_pose.v[2]));

    // Motion model update
    impl_->motion_model->odometryUpdate(impl_->pf, pose, delta);

    // Prepare laser data with memory-safe operations
    LaserData ldata;
    ldata.laser = impl_->laser.get();
    ldata.range_count = static_cast<int>(scan.ranges.size());
    ldata.range_max = scan.range_max;

    // Use persistent buffer to avoid memory issues
    impl_->ranges_buffer = scan.ranges;
    ldata.ranges = reinterpret_cast<double(*)[2]>(impl_->ranges_buffer.data());

    // Sensor update
    impl_->laser->sensorUpdate(impl_->pf, &ldata);
    
    // Prevent LaserData destructor from trying to delete[] our std::vector managed memory
    ldata.ranges = nullptr;
    
    // Update particle filter
    pf_update_resample(impl_->pf, impl_->map);
    impl_->odom_pose = pose;
}

Vector3D AMCL::getPoseMean() const {
    if (!impl_->pf) {
        throw std::runtime_error("Particle filter not initialized");
    }
    
    pf_sample_set_t* set = impl_->pf->sets + impl_->pf->current_set;
    return Vector3D(set->mean.v[0], set->mean.v[1], set->mean.v[2]);
}

Matrix3D AMCL::getPoseCovariance() const {
    if (!impl_->pf) {
        throw std::runtime_error("Particle filter not initialized");
    }
    
    pf_sample_set_t* set = impl_->pf->sets + impl_->pf->current_set;
    Matrix3D cov;
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
            cov.m[i][j] = set->cov.m[i][j];
        }
    }
    return cov;
}

void AMCL::setInitialPose(const Vector3D& pose, const Matrix3D& cov) {
    if (!impl_->pf) {
        throw std::runtime_error("Particle filter not initialized");
    }
    
    pf_vector_t mean;
    mean.v[0] = pose.v[0];
    mean.v[1] = pose.v[1];
    mean.v[2] = pose.v[2];

    pf_matrix_t p_cov;
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
            p_cov.m[i][j] = cov.m[i][j];
        }
    }

    pf_init(impl_->pf, mean, p_cov);
    impl_->pf_init = false;
}

void AMCL::setLaserPose(const Vector3D& laser_pose) {
    if (!impl_->laser) {
        throw std::runtime_error("Laser sensor not initialized");
    }
    
    pf_vector_t pose;
    pose.v[0] = laser_pose.v[0];
    pose.v[1] = laser_pose.v[1];
    pose.v[2] = laser_pose.v[2];
    
    impl_->laser->SetLaserPose(pose);
}

bool AMCL::isInitialized() const {
    return impl_ && impl_->pf_init;
}

} // namespace nav2_amcl