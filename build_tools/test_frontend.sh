#!/bin/bash

# This script is meant to be run from the script step in .travis.yml
# The tests run by this script are "frontend" testing

LOG="/tmp/frontend_test_hub.log"
FAIL=0
NPROC=2

echo "In" `pwd`

# Start a hub that our tests can interact with
echo "Starting everware"

OPTS="-f build_tools/frontend_test_config.py --no-ssl --debug"
everware-server ${OPTS} > $LOG 2>&1 &
HUB_PID=$!
sleep 3

if [ `pgrep -f jupyterhub` == "" ] ; then echo "Error starting" && exit 1 ; fi

echo "Start running frontend tests"
if [ -z "$UPLOADDIR" ] ; then 
	echo "no UPLOADDIR defined" 
	kill ${HUB_PID}
	exit 1
fi
[ -d $UPLOADDIR ] && rm -rf $UPLOADDIR/*
nose2 -v -N $NPROC --start-dir=frontend_tests || FAIL=1

if [ -f $LOG ]; then
    echo ">>> Frontend test hub log:"
    cat $LOG
    echo "<<< Frontend test hub log:"
    docker ps -a
fi

kill ${HUB_PID}
exit $FAIL
