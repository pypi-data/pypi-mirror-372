import logging
import os
import subprocess
from pathlib import Path
from typing import Callable, List, Optional
from uuid import uuid4

from kognic.io.tools.calibration.exceptions import CompilationError, CompilationOutputError
from kognic.io.tools.calibration.validation import FUNCTION_NAME, validate_wasm_binary

logger = logging.getLogger(__name__)


COMPILE_FUNCTION = Callable[[Path, Path], None]


def compile_to_wasm(*, input_path: Path, output_wasm: Optional[Path] = None, skip_validation: bool = False) -> bytes:
    """
    Compile a source file to a wasm binary.

    :param input_path: Path to the source file. See documentation for supported file types
    :param output_wasm: Path to the output wasm file. If not specified, a temporary file will be created and deleted
        after compilation
    :param skip_validation: If True, the compiled wasm binary will not be validated
    :return: The compiled wasm binary
    """

    if not input_path.exists():
        raise FileNotFoundError(f"File not found: {input_path}")

    if output_wasm is not None and output_wasm.suffix != ".wasm":
        raise CompilationOutputError(f"Output should be a wasm file, got {output_wasm}")

    clean_up = output_wasm is None  # If no output file is specified, we clean up the generated wasm file
    output_wasm = output_wasm or Path(f"{uuid4()}.wasm")

    if output_wasm.exists():
        logger.warning(f"Output file {output_wasm} already exists, overwriting")
        output_wasm.unlink()

    try:
        wasm = _compile(input_path, output_wasm)
    except Exception as e:
        raise CompilationError(f"Failed to compile {input_path}") from e

    if skip_validation is False:
        validate_wasm_binary(wasm, test_cases=[])

    if clean_up:
        output_wasm.unlink()

    return wasm


def _compile(input_file: Path, output_wasm: Path) -> bytes:
    if input_file.name == "Cargo.toml":
        _compile_rust_cargo(input_file, output_wasm)
    elif input_file.suffix == ".rs":
        _compile_rust(input_file, output_wasm)
    elif input_file.suffix in [".cc", ".cpp"]:
        _compile_cpp(input_file, output_wasm)
    elif input_file.suffix == ".c":
        _compile_c(input_file, output_wasm)
    else:
        raise ValueError(f"File {input_file} not supported")
    return output_wasm.read_bytes()


def _compile_rust(input_file: Path, output_file: Path):
    logger.info("Compiling Rust file to Webassembly")

    cmd = [
        "rustc",
        "-v",
        "--crate-type=cdylib",
        "-Copt-level=3",
        "-Cstrip=symbols",
        "--target=wasm32-wasip1",
        "-Ctarget-feature=+multivalue",
        str(input_file),
        f"-o{output_file}",
    ]
    _run_command(cmd)


def _compile_rust_cargo(input_file: Path, output_file: Path):
    logger.info("Compiling Rust with Cargo to Webassembly")
    if os.environ.get("RUSTFLAGS") is None:
        # Note: This is required to enable multivalue support in Rust with Cargo
        os.environ["RUSTFLAGS"] = "-C target-feature=+multivalue"

    cmd = [
        "cargo",
        "build",
        "--release",
        "--target=wasm32-wasip1",
        f"--manifest-path={input_file}",
    ]
    _run_command(cmd)

    # Copy the compiled wasm file to the output file

    wasm_name = input_file.parent.stem.replace("-", "_") + ".wasm"
    compiled_wasm_file = input_file.parent / f"target/wasm32-wasip1/release/{wasm_name}"
    assert compiled_wasm_file.exists(), f"Compiled wasm file not found at {compiled_wasm_file}"
    logger.info(f"Copying compiled wasm file from {compiled_wasm_file} to {output_file}")
    os.system(f"cp {compiled_wasm_file} {output_file}")


def _compile_cpp(input_file: Path, output_file: Path):
    logger.info("Compiling C++ file to Webassembly")
    _compile_with_emscripten(input_file, output_file)


def _compile_c(input_file: Path, output_file: Path):
    logger.info("Compiling C file to Webassembly")
    _compile_with_emscripten(input_file, output_file)


def _compile_with_emscripten(input_file: Path, output_file: Path):
    cmd = [
        "emcc",
        "-mmultivalue",
        "-Xclang",
        "-target-abi",
        "-Xclang",
        "experimental-mv",
        "-Oz",
        "-sSTANDALONE_WASM",
        f'-sEXPORTED_FUNCTIONS=["_{FUNCTION_NAME}"]',
        "-Wl,--no-entry",
        str(input_file),
        f"-o{output_file}",
    ]
    _run_command(cmd)


def _run_command(cmd: List[str]) -> None:
    logger.info(f"Running command: {' '.join(cmd)}")
    try:
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError as e:
        logger.error("Failed to compile to wasm")
        raise e
