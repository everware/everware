#!/bin/bash

# This script is meant to be run from the script step in .travis.yml
# The tests run by this script are "frontend" testing

LOG="/tmp/frontend_test_hub.log"
FAIL=0
NPROC=2

echo "In" `pwd`

OPTS="-f build_tools/frontend_test_config.py --no-ssl --debug $1"
NONSTOP_OPTS="-f build_tools/nonstop_frontend_test_config.py --no-ssl --debug $1"

docker ps -a -q | sort >old_cont

# Start a hub that our tests can interact with
echo "Starting everware-server($OPTS)"
everware-server ${OPTS} > $LOG 2>&1 &
sleep 3

if [[ `pgrep -f everware-server` == "" ]] ; then
    echo "Error starting"
    tail $LOG
    exit 1
fi

echo "Start running frontend tests"
if [ -z "$UPLOADDIR" ] ; then
	echo "no UPLOADDIR defined"
    pkill -f everware-server
    pkill -f node
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

ADDED_CONT=0

docker ps -a -q | sort >new_cont
diff old_cont new_cont || ADDED_CONT=1

if [ $ADDED_CONT -eq 1 ]; then
    FAIL=1
    echo "Old containers:"
    cat old_cont
    echo "New containers:"
    cat new_cont
fi

rm old_cont new_cont
pkill -f everware-server
pkill -f node
if [ $FAIL -eq 1 ]; then
    exit $FAIL
fi
sleep 15

# spawn container to substitute in tests
echo "Spawning running container"
docker run --name jupyter-user1 --rm busybox sh -c 'sleep 3600' &

echo "Starting everware-server($NONSTOP_OPTS)"
everware-server ${NONSTOP_OPTS} > $LOG 2>&1 &

if [[ `pgrep -f everware-server` == "" ]] ; then
    echo "Error starting (non stop)"
    tail $LOG
    exit 1
fi

sleep 3
export NOT_REMOVE=1

nose2 -v -N $NPROC --start-dir=frontend_tests || FAIL=1

if [ -f $LOG ]; then
    echo ">>> Frontend test hub log (not remove containers):"
    cat $LOG
    echo "<<< Frontend test hub log (not remove containers):"
fi


echo ">>> Frontend test client log"
find $UPLOADDIR -name "*.log" | xargs cat
echo "<<< Frontend test client log"

pkill -f everware-server
pkill -f node
exit $FAIL
