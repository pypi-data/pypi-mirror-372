#include <limits>

// Define calibration model
struct tuple { double x; double y; };

struct CameraMatrix {
    double fx;
    double fy;
    double cx;
    double cy;
};

struct DistortionCoefficients {
    double k1;
    double k2;
    double p1;
    double p2;
    double k3;
};

static const CameraMatrix CAMERA_MATRIX = {
    2598.949951171875,
    2598.949951171875,
    4612.0,
    1672.0
};

static const DistortionCoefficients DISTORTION_COEFFICIENTS = {
    0.0,
    0.0,
    0.0,
    0.0,
    0.0
};

tuple run_projection(double x, double y, double z) {

    if (z <= 0.0) {
        const auto nan = std::numeric_limits<double>::quiet_NaN();
        return {nan, nan};
    }

    const auto xp = x / z;
    const auto yp = y / z;

    const auto xp2 = xp * xp;
    const auto yp2 = yp * yp;

    const auto r2 = xp2 + yp2;
    const auto r4 = r2 * r2;
    const auto r6 = r4 * r2;

    const auto& dc = DISTORTION_COEFFICIENTS;
    const auto kr = 1.0 + dc.k1 * r2 + dc.k2 * r4 + dc.k3 * r6;
    const auto u = xp * kr + 2.0 * dc.p1 * xp * yp + dc.p2 * (r2 + 2.0 * xp2);
    const auto v = yp * kr + dc.p1 * (r2 + 2.0 * yp2) + 2.0 * dc.p2 * xp * yp;

    const auto& c = CAMERA_MATRIX;
    return {c.fx * u + c.cx, c.fy * v + c.cy};
}

// Exported function
extern "C" {
    tuple project_point_to_image(const double x, const double y, const double z) {
        return run_projection(x, y, z);
    }
}


