# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Installation and Setup

Where possible use `uv` to manage the environment (if `UV_ENABLED` is set or `uv` is available already).

**Step 1: Create virtual environment**
- A Python 3.9+ (ideally 3.12+) venv is required. A new clean venv is recommended.
- `uv venv --python 3.12` (or use `python3 -m venv .venv` if uv unavailable)
- `source .venv/bin/activate`

**Step 2: Kognic-specific setup** (one-time setup steps):
- GCP command line tool `gcloud` is needed. 
- If not auth'd with gcloud yet then `gcloud auth application-default login`
- `uv pip install --index-url https://pypi.python.org/simple kognic-keyring` (use `pip` instead of `uv pip` if uv unavailable)
- `pip config set global.index-url https://oauth2accesstoken@pypi.kognic.io/simple`

**Step 3: Install packages**
- `uv pip install -e .`
- `uv pip install -r requirements-dev.txt`
- `uv pip install -e .[wasm]`
- Custom camera calibrations WASM features may require external dependencies/tools: cargo, rust and emscripten, which need to be installed separately.

### Testing

- Most tests are integration tests that are intended to run against staging in order to validate before release.
- These can also run against a local development environment which requires the developer to set up a local compose environment.
- Running tests needs a credentials file, normally from `~/.config/kognic/*.json` which is set in `KOGNIC_CREDENTIALS` env var.
- e.g. `KOGNIC_CREDENTIALS=~/.config/kognic/credentials-staging.json pytest --env staging`
- Where possible prefer to run one test method or class at a time to keep the dev cycle short.

Most integration tests run `examples/` code fragments to get their logic done. The examples are synced into our public 
docs. This means the examples are kept runnable and updated.

### WASM Development

- run the responsible python test to check WASM-related features.

## Architecture Overview

### Core Client Structure
The main entry point is `KognicIOClient` in `src/kognic/io/client.py`, which provides access to all platform resources through specialized resource classes.

### Resource Pattern
The codebase follows a consistent resource pattern where each domain has:
- **Resource classes** (`*Resource`): API interaction layer in `src/kognic/io/resources/`
- **Model classes**: Data models in `src/kognic/io/model/`
- **Abstract base classes**: `IOResource` and `CreatableIOResource` in `src/kognic/io/resources/abstract/`

### Key Resource Types
- **Scene Resources**: Handle different sensor configurations (cameras, lidars, sequences)
  - `SceneResource`: General scene operations
  - `Cameras`, `Lidars`, `LidarsAndCameras`: Single-frame sensor data
  - `*Sequence` variants: Multi-frame sensor sequences. `LidarsAndCamerasSequence` is commonly referred to as "LACS".
  - `AggregatedLidarsAndCamerasSequence`: aka "ALCS". These are really just LACS with a hint to the platform to use aggregation features.
- **Input/Output Resources**: `InputResource`, `AnnotationResource`, `PreAnnotationResource`
- **Project Resources**: `ProjectResource`, workspace and batch management
- **Calibration Resources**: `CalibrationResource` with WASM-based custom camera calibrations

### Data Models Structure
- **Scene models**: Different sensor configurations in `src/kognic/io/model/scene/`
- **Input models**: Input creation and management in `src/kognic/io/model/input/`
- **Calibration models**: Camera and LiDAR calibrations in `src/kognic/io/model/calibration/`
- **Ego models**: Vehicle pose and IMU data in `src/kognic/io/model/ego/`

### Custom Camera Calibrations
The system supports custom camera calibrations via WebAssembly:
- Compilation tools in `src/kognic/io/tools/calibration/`
- Supports C, C++, and Rust source files
- WASM binaries are validated before use
- CLI tools available via `kognicutil wasm` commands

## File Organization
- `src/kognic/io/`: Main package code
- `examples/`: Usage examples (automatically synced to public repository)
- `tests/`: Test suite with markers for integration and WASM tests
- `bin/kognicutil`: seldom-touched CLI utility script

## Development Notes
- Line length limit: 140 characters (configured in pyproject.toml)
- Python 3.9+ required, 3.10+ is better, 3.12+ is ideal.
- Examples are publicly visible and automatically synced, ensure they don't leak sensitive information like customer names or identifiers.
- Run `black .` and `ruff check --fix .` to format and lint the code. Do this after each set of modifications; at least once before commit.
- When writing code prefer to split e.g. method calls and signatures into multiple lines only when black/ruff insist. 
- When adding a class to model packages, expose it via imports in `__init__.py` but do not add a `def __all__()`. 

## Comments

- Write comments sparingly, where it's necessary to explain the code.
- Don't put content in comments that can rot easily when other code changes like "this impl is stricter than OtherClass".
- Comments should never repeat or interpret the code into english, e.g. "// Get the user" followed by getUser(1)
- We don't write step-by-step comments to explain how the code works, as the code should be self-explanatory. 
- Other inline comments `# ...` explain non-obvious situations, workarounds, context that might be lost.
- TODOs are OK to commit if we'll get to them soon. Not stuff for an ideal world.
- Don't put comments in tests that just outline the test structure, "set up data", "mock responses", "assert result", etc.
- As this is a public client library, `"""` docstrings are important, but they do not need to be exhaustive. What does the method do, what are the params, any special cases, etc.
