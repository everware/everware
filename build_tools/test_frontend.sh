#!/bin/bash

# This script is meant to be run from the script step in .travis.yml
# The tests run by this script are "frontend" testing

LOG="/tmp/frontend_test_hub.log"
NPROC=2
TESTS_DIR="frontend_tests"
WAIT_FOR_START=3
WAIT_FOR_STOP=25

function kill_everware {
    echo "Stopping everware"
    pkill -TERM -f everware-server
    sleep $WAIT_FOR_STOP
}

if [ -z "$UPLOADDIR" ] ; then
	echo "no UPLOADDIR defined"
	exit 1
fi
[ -d "$UPLOADDIR" ] && rm -rf "$UPLOADDIR"/*

echo "Start running frontend tests"

for run_type in "normal" "nonstop"; do
    SCENARIOS=`python3 $TESTS_DIR/test_generator.py $run_type`
    RUN_OPTIONS="-f build_tools/frontend_test_${run_type}_config.py --no-ssl --debug $1"
    echo "Running $run_type scenarios"

    for scenario in ${SCENARIOS}; do
        echo "Running scenario $scenario"
        everware-server $RUN_OPTIONS > $LOG 2>&1 &
        sleep $WAIT_FOR_START
        if [[ -z `pgrep -f everware-server` ]] ; then
            echo "Error starting"
            tail $LOG
            exit 1
        fi

        export EVERWARE_MODULE=$run_type
        export EVERWARE_SCENARIO=$scenario
        nose2 -v -N $NPROC --start-dir=$TESTS_DIR || FAIL=1
        if [[ $FAIL -eq 1 ]]; then
            kill_everware
            echo ">>> Frontend test hub log:"
            cat $LOG
            echo "<<< Frontend test hub log:"
            exit $FAIL
        fi

        kill_everware
        if [[ -n `pgrep -f everware-server` ]]; then
            echo "Error stopping"
            cat $LOG
            exit 1
        fi
    done
done


