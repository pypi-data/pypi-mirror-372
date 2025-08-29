import logging
from pathlib import Path

import click

from kognic.io.tools.calibration.compilation import compile_to_wasm
from kognic.io.tools.calibration.validation import validate_wasm_file


@click.group(name="wasm")
def cli():
    """Commands related to custom camera calibrations using WebAssembly"""
    logging.basicConfig(level=logging.INFO)


@click.command(help="Compile source to WebAssembly binary.")
@click.argument("src-file", type=Path)
@click.argument("output-file", type=Path)
@click.option("--skip-validation", is_flag=True, show_default=True)
def compile(src_file: Path, output_file: Path, skip_validation: bool):
    print(f"Compiling {src_file} to {output_file}")
    compile_to_wasm(input_path=src_file, output_wasm=output_file, skip_validation=skip_validation)
    print(f"Successfully compiled {src_file} to {output_file}")


@click.command(help="Validate wasm binary")
@click.argument("wasm-file", type=Path)
def validate(wasm_file: Path):
    print(f"Validating {wasm_file}")
    validate_wasm_file(wasm_file, list())
    print("Wasm file successfully validated")


cli.add_command(compile)
cli.add_command(validate)

if __name__ == "__main__":
    cli()
