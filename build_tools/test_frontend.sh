#!/bin/bash

# This script is meant to be run from the script step in .travis.yml
# The tests run by this script are "frontend" testing

LOG="/tmp/frontend_test_hub.log"
FAIL=0
NPROC=2

echo "In" `pwd`

OPTS="-f build_tools/frontend_test_config.py --no-ssl --debug $1"

docker ps -a -q | sort >old_cont

# Start a hub that our tests can interact with
echo "Starting everware-server($OPTS)"
everware-server ${OPTS} > $LOG 2>&1 &
HUB_PID=$!
sleep 3

if [[ `pgrep -f everware-server` == "" ]] ; then 
    echo "Error starting"
    tail $LOG 
    exit 1
fi

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

ADDED_CONT=0

# echo ">>>>>>> Checking sleep container"
# docker ps -a -q | head -1 | xargs docker inspect
# docker ps -a -q | head -1 | xargs docker logs
# echo "<<<<<<< Done"

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

echo ">>> Frontend test client log"
find $UPLOADDIR -name "*.log" | xargs cat
echo "<<< Frontend test client log"

kill ${HUB_PID}
exit $FAIL
