import logging
import math
import os
from pathlib import Path
from typing import List, Tuple

from wasmtime import Func, FuncType, Instance, Module, Store, ValType

from kognic.io.model.calibration.camera.custom_camera_calibration import CustomCameraCalibration, TestCase
from kognic.io.tools.calibration.exceptions import (
    FunctionNotFoundError,
    FunctionSignatureError,
    LoadingError,
    ProjectionError,
    ProjectionValidationError,
)

logger = logging.getLogger(__name__)

FUNCTION_NAME = "project_point_to_image"
TOLERANCE = 1e-5
BASE_POINT = (1.0, 2.0, 1.0)  # all wasm modules should be able to project this point successfully


def validate_custom_camera_calibration(calibration: CustomCameraCalibration) -> None:
    """
    Validate a custom camera calibration by loading it and running some basic tests.

    :param calibration: The custom camera calibration
    """
    wasm_bytes = calibration.get_wasm_bytes()
    validate_wasm_binary(wasm_bytes, calibration.test_cases)


def validate_wasm_file(wasm_file: Path, test_cases: List[TestCase]) -> None:
    """
    Validate a wasm file by loading it and running some basic tests.

    :param wasm_file: The wasm file
    :param test_cases: A list of test cases to validate the wasm binary
    """
    logger.info(f"Validating {wasm_file}")

    with open(wasm_file, "rb") as f:
        wasm_bytes = f.read()

    return validate_wasm_binary(wasm_bytes, test_cases)


def validate_wasm_binary(wasm: bytes, test_cases: List[TestCase]) -> None:
    """
    Validate a wasm binary by loading it and running some basic tests.

    :param wasm: The wasm binary
    :param test_cases: A list of test cases to validate the wasm binary
    """
    logger.info("Validating wasm binary")

    wasm_size = os.path.getsize(wasm) if isinstance(wasm, Path) else len(wasm)
    if wasm_size > 1000:
        logger.warning(
            f"Wasm has a size of {wasm_size} bytes which is greater than the normal 1kB. This is an "
            f"indication that something could have gone wrong during compilation"
        )
    else:
        logger.info(f"Wasm file has a size of {wasm_size} bytes")

    function = _load_function(wasm, FUNCTION_NAME)
    _validate_function_signature(function.function.type(function.store))
    _validate_basic_projection(function)
    _validate_test_cases(function, test_cases)

    logger.info("Wasm file successfully validated")


class ProjectionFunction:
    def __init__(self, function: Func, store: Store):
        self.function = function
        self.store = store

    def __call__(self, x: float, y: float, z: float) -> Tuple[float, float]:
        return self.function(self.store, x, y, z)


def _load_function(wasm: bytes, function_name: str) -> ProjectionFunction:
    try:
        store = Store()
        module = Module(store.engine, wasm=wasm)
        instance = Instance(store, module, module.imports)
    except Exception as e:
        raise LoadingError(f"Could not load wasm binary: {e}") from e

    try:
        exports = instance.exports(store)._extern_map
    except AttributeError:
        exports = instance.exports(store).extern_map

    if function_name not in exports:
        raise FunctionNotFoundError(f"Did not find function {function_name} in wasm module")

    return ProjectionFunction(function=exports[function_name], store=store)


def _validate_function_signature(function_signature: FuncType) -> None:
    f64 = ValType.f64()
    params = function_signature.params
    results = function_signature.results

    if params != [f64, f64, f64] or results != [f64, f64]:
        raise FunctionSignatureError(
            f"The function should have signature (f64, f64, f64) => (f64, f64), not {tuple(params)} => {tuple(results)}"
        )


def _validate_basic_projection(function: ProjectionFunction) -> None:
    try:
        (u, v) = function(*BASE_POINT)
        assert isinstance(u, float) and isinstance(v, float), f"Expected floats, got ({type(u)}, {type(v)})"
        logger.debug(f"Successfully projected point {BASE_POINT} to ({u}, {v})")
    except Exception as e:
        raise ProjectionError(f"Could not project base point {BASE_POINT}: {e}") from e


def _validate_test_cases(function: ProjectionFunction, test_cases: List[TestCase]) -> None:
    for test_case in test_cases:
        point, expected = test_case.point3d, test_case.point2d
        (u, v) = function(point.x, point.y, point.z)

        if not _are_equal(u, expected.x) or not _are_equal(v, expected.y):
            raise ProjectionValidationError(
                f"Expected ({expected.x}, {expected.y}), but got ({u}, {v}) for point ({point.x}, {point.y}, {point.z})"
            )


def _are_equal(a: float, b: float) -> bool:
    if math.isnan(a) and math.isnan(b):
        return True
    return abs(a - b) < TOLERANCE
