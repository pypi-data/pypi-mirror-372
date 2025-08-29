#include <math.h>
#include <float.h>

// Define calibration model
struct tuple {
    double x;
    double y;
};

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

static const struct CameraMatrix CAMERA_MATRIX = {
    2598.949951171875,
    2598.949951171875,
    4612.0,
    1672.0
};

static const struct DistortionCoefficients DISTORTION_COEFFICIENTS = {
    0.0,
    0.0,
    0.0,
    0.0,
    0.0
};

struct tuple run_projection(double x, double y, double z) {
    if (z <= 0.0) {
        const double nan = NAN;
        return (struct tuple){nan, nan};
    }

    const double xp = x / z;
    const double yp = y / z;

    const double xp2 = xp * xp;
    const double yp2 = yp * yp;

    const double r2 = xp2 + yp2;
    const double r4 = r2 * r2;
    const double r6 = r4 * r2;

    const struct DistortionCoefficients dc = DISTORTION_COEFFICIENTS;
    const double kr = 1.0 + dc.k1 * r2 + dc.k2 * r4 + dc.k3 * r6;
    const double u = xp * kr + 2.0 * dc.p1 * xp * yp + dc.p2 * (r2 + 2.0 * xp2);
    const double v = yp * kr + dc.p1 * (r2 + 2.0 * yp2) + 2.0 * dc.p2 * xp * yp;

    const struct CameraMatrix c = CAMERA_MATRIX;
    return (struct tuple){c.fx * u + c.cx, c.fy * v + c.cy};
}

// Exported function
struct tuple project_point_to_image(const double x, const double y, const double z) {
    return run_projection(x, y, z);
}