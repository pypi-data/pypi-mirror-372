# Kognic IO Client

Python 3 library providing access to Kognic IO. This package is public and available on [PyPi](https://pypi.org/project/kognic-io/).

Note that any changes to the examples are automatically pushed [kognic-io-python-examples](https://github.com/annotell/kognic-io-examples-python/tree/master), which is a **public** repository.
This is where the examples in the documentation are taken from.

## Installation

To install the latest public version, run `pip install kognic-io`.

For local development it is recommended to install locally with `pip install -e .` in the root folder.

## Documentation

The public documentation is hosted by the [public-docs](https://github.com/annotell/public-docs) repository and publicly available [here](https://docs.kognic.com/).

## Testing

### Requirements

Some tests require extra dependencies. To install them, run `pip install -r requirements-dev.txt`.

### Environment

Most tests are integration tests and require a valid credentials file to the specific environment. The environment is
specified by the `--env` flag and can be either `development` or `staging`. The default is `development`.
Note that `KOGNIC_CREDENTIALS` needs to be set to a valid credentials file for the environment you are testing against.

### Markers

Some tests have markers since they have dependencies that are not always available. The markers are `wasm` and
`integration`. The `integration` marker is used for tests that require a valid credentials file to the specific environment. 
These are not run in CI.  The `wasm` marker is used for tests that require kognic-io to be installed with `wasm` support
and some extra language-specific dependencies (for example `cargo`for Rust). More about language-specific dependencies
can be found in the [public documentation](https://docs.kognic.com/api-guide/custom-camera-calibrations#8P4tM).

### Running tests

The tests can be run against different environments and with different markers, see examples below.

```bash
pytest ./tests # all tests against development
pytest --env=staging ./tests # all tests against staging
pytest -m 'not wasm' ./tests # all tests except wasm
pytest -m 'wasm' ./tests # only wasm tests
pytest -m 'not integration' ./tests # all tests except integration
pytest -m 'not wasm and not integration' ./tests # all tests except wasm and integration
```

## Releasing

Releasing new versions of the package is done by creating a git tag. This will trigger a GitHub action that will build
and publish the package to PyPi. The version number is determined by the git tag, so make sure to use the correct format
when creating a new tag. The format is `vX.Y.Z` where `X`, `Y` and `Z` are integers. To create a new tag and push it to
the remote repository, run the following commands

```bash
git tag vX.Y.Z; git push origin vX.Y.Z
```

**Important:** Don't forget to update the changelog with the new version number and a description of the changes before
releasing a new version. The changelog is located in the root folder and is named `CHANGELOG.md`.

### Release candidates

Sometimes you want people other than developer to try out the release. For this purpose you can use a release candidate which can be done in a branch.

Once you're happy with you branch and want to release it run

```bash
git tag vX.Y.Z-RC1; git push origin vX.Y.Z-RC1
```

This will publish a prerelease `kognic-io==vX.Y.Zrc1` to pypi. It will not be install unless it's explicitly specified.