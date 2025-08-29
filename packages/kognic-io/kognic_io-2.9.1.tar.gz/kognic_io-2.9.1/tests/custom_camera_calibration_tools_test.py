from pathlib import Path

import pytest
from click.testing import CliRunner

import kognic.io.kognicutil as kognicutil
from examples.calibration.create_custom_camera_calibration import example_custom_camera_calibration
from kognic.io.model.calibration.camera.custom_camera_calibration import Point2d, Point3d, TestCase
from kognic.io.model.calibration.camera.custom_camera_calibration import TestCase as WasmTestCase
from kognic.io.tools.calibration.exceptions import ProjectionValidationError

try:
    # We cannot import this if wasmtime is not installed
    from kognic.io.tools.calibration.compilation import compile_to_wasm
    from kognic.io.tools.calibration.validation import validate_custom_camera_calibration, validate_wasm_binary, validate_wasm_file
except ImportError:
    print("WARNING: Cannot run tests for custom camera calibration tools. Install with wasm to run these tests.")


@pytest.mark.wasm  # Requires wasmtime to be run
class TestCustomCameraCalibrationValidation:
    def test_custom_camera_calibration_validation(self):
        custom_camera_calibration = example_custom_camera_calibration()
        validate_custom_camera_calibration(custom_camera_calibration)

    def test_custom_camera_calibration_validation_file(self):
        custom_camera_calibration = example_custom_camera_calibration()
        path = Path("./examples/resources/pinhole.wasm")
        validate_wasm_file(path, custom_camera_calibration.test_cases)

    def test_custom_camera_calibration_validation_raises(self):
        custom_camera_calibration = example_custom_camera_calibration()
        # Set invalid expected values
        test_case = custom_camera_calibration.test_cases[0]
        custom_camera_calibration.test_cases[0] = WasmTestCase(point3d=test_case.point3d, point2d=Point2d(x=0, y=0))
        with pytest.raises(ProjectionValidationError) as e:
            validate_custom_camera_calibration(custom_camera_calibration)
        assert e.value.args[0] == "Expected (0.0, 0.0), but got (3411.3379681991337, 1457.470078963514) for point (3.0, 1.0, 4.0)"


@pytest.mark.wasm
class TestCustomCameraCalibrationCompilation:
    @staticmethod
    def compile_with_cli(example_path: Path):
        runner = CliRunner()
        output_path = example_path.name + ".wasm"
        result = runner.invoke(kognicutil.wasm_cli, ["compile", str(example_path), output_path])
        assert result.exit_code == 0, result.output

    def test_compile_rust_example_with_cli(self):
        self.compile_with_cli(Path("./examples/calibration/custom/pinhole.rs"))

    def test_compile_rust_cargo_example_with_cli(self):
        self.compile_with_cli(Path("./examples/calibration/custom/pinhole-rust-cargo/Cargo.toml"))

    def test_compile_cpp_example_with_cli(self):
        self.compile_with_cli(Path("./examples/calibration/custom/pinhole.cc"))

    def test_compile_c_example_with_cli(self):
        self.compile_with_cli(Path("./examples/calibration/custom/pinhole.c"))

    @staticmethod
    def run_compilation_and_validate_result(example_path: Path):
        wasm_binary = compile_to_wasm(input_path=example_path)
        assert wasm_binary is not None

        test_cases = [
            TestCase(point3d=Point3d(x=3, y=1, z=4), point2d=Point2d(x=6561.212463378906, y=2321.7374877929688)),
            TestCase(point3d=Point3d(x=1, y=5, z=-9), point2d=Point2d(x=float("nan"), y=float("nan"))),
        ]

        res = validate_wasm_binary(wasm_binary, test_cases)
        assert res is None

    def test_compile_rust_example(self):
        self.run_compilation_and_validate_result(Path("./examples/calibration/custom/pinhole.rs"))

    def test_compile_rust_cargo_example(self):
        self.run_compilation_and_validate_result(Path("./examples/calibration/custom/pinhole-rust-cargo/Cargo.toml"))

    def test_compile_cpp_example(self):
        self.run_compilation_and_validate_result(Path("./examples/calibration/custom/pinhole.cc"))

    def test_compile_c_example(self):
        self.run_compilation_and_validate_result(Path("./examples/calibration/custom/pinhole.c"))
