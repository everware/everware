#!/bin/bash

# This script is meant to be run from the script step in .travis.yml
# The tests run by this script are "frontend" testing

LOG="/tmp/frontend_test_hub.log"

echo "In" `pwd`

# Start a hub that our tests can interact with
echo "Starting everware"

# XXX Latest release does not yet force SSL
if [[ "$JHUB_VERSION" == "latest" ]]; then
    OPTS="-f build_tools/frontend_test_config.py --debug"
else
    OPTS="-f build_tools/frontend_test_config.py --no-ssl --debug"
fi
jupyterhub ${OPTS} > $LOG 2>&1 &
HUB_PID=$!
sleep 3

echo "Start running frontend tests"
[ -d $UPLOADDIR ] && rm -rf $UPLOADDIR/*
nose2 -v --start-dir frontend_tests

if [ -f $LOG ]; then
    echo ">>> Frontend test hub log:"
    cat $LOG
    echo "<<< Frontend test hub log:"
fi

kill ${HUB_PID}
