// Define calibration model
struct CameraMatrix { fx: f64, fy: f64, cx: f64, cy: f64, }
struct DistortionCoefficients { k1: f64, k2: f64, p1: f64, p2: f64, k3: f64, }

static CAMERA_MATRIX: CameraMatrix = CameraMatrix {
    fx: 2598.949951171875,
    fy: 2598.949951171875,
    cx: 4612.0,
    cy: 1672.0,
};

static DISTORTION_COEFFICIENTS: DistortionCoefficients = DistortionCoefficients {
    k1: 0.0,
    k2: 0.0,
    k3: 0.0,
    p1: 0.0,
    p2: 0.0
};

/* Exported function */
#[no_mangle]
pub unsafe fn project_point_to_image(x: f64, y: f64, z: f64) -> (f64, f64) {
    if z <= 0.0 {
        return (f64::NAN, f64::NAN); // Point is behind the camera => not in FoV
    }

    let xp = x / z;
    let yp = y / z;

    let xp2 = xp * xp;
    let yp2 = yp * yp;

    let r2 = xp2 + yp2;
    let r4 = r2 * r2;
    let r6 = r4 * r2;

    let dc = &DISTORTION_COEFFICIENTS;
    let kr = 1.0 + dc.k1 * r2 + dc.k2 * r4 + dc.k3 * r6;
    let u = xp * kr + 2.0 * dc.p1 * xp * yp + dc.p2 * (r2 + 2.0 * xp2);
    let v = yp * kr + dc.p1 * (r2 + 2.0 * yp2) + 2.0 * dc.p2 * xp * yp;

    let c = &CAMERA_MATRIX;
    (c.fx * u + c.cx, c.fy * v + c.cy)
}
