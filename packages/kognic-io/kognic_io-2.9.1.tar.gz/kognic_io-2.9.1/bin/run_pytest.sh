#!/usr/bin/env bash

# Prerequisites:
#
Help()
{
# Display Help
  echo "runs pytest from the commandline in order to run all io_client tests"
    echo
    echo "Syntax: run_pytest [--env]"
    echo "options:"
    echo "--help           Shows this helpful text"
    echo "--env            Sets the environment to run integration tests towards."
    echo "                 Possible values are: [development, staging]"
    echo
}

ENV=""
ROOT_DIR=""
while (( "$#" )); do
  case "$1" in
    --env)
      shift
      ENV="$1"
      shift
      ;;
    --rootdir)
      ROOT_DIR="$1"
      shift
      ;;
     --help)
      Help
      exit 0
      ;;
    -*|--*) # unsupported flags
      echo "Error: Unsupported flag $1" >&2
      echo "Try running with --help to see help text" >&2
      exit 1
      ;;
    *) # we don't take any arguments
      echo "Error: Unsupported argument $1" >&2
      echo "Try running with --help to see help text" >&2
      exit 1
      ;;
  esac
done

if [ -z $ENV ]; then
  pytest --rootdir="./tests/"
else
  pytest --rootdir="./tests/" --env=$ENV
fi

exit 0
