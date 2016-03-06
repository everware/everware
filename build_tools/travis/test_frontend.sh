#!/bin/bash

# This script is meant to be run from the script step in .travis.yml
# The tests run by this script are "frontend" testing

set -e

# Start a hub that our tests can interact with
jupyterhub -f build_tools/travis/frontend_test_config.py --no-ssl --debug
sleep 3
nose2 -v --start-dir frontend_tests -N 2 test_happy_mp
