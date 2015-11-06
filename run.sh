#!/bin/bash
set -e

source env.sh
OPTIONS="--debug"

jupyterhub $OPTIONS
