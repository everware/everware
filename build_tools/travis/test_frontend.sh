#!/bin/bash

# This script is meant to be run from the script step in .travis.yml
# The tests run by this script are "frontend" testing

set -e
echo "In" `pwd`

# Start a hub that our tests can interact with
echo "Starting everware"
jupyterhub -f build_tools/travis/frontend_test_config.py \
           --no-ssl --debug > /tmp/hub.txt 2>&1 &
sleep 3

echo "Start running frontend tests"
nose2 -v --start-dir frontend_tests

echo ">>> Logging output of jupyterhub"
cat /tmp/hub.log
echo "<<< Logging output of jupyterhub"
