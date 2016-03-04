#!/bin/bash
set -e

source ./env.sh
OPTIONS="--debug --port 8000 --log-file=jupyterhub.log --no-ssl"
source ./clean.sh

jupyterhub $OPTIONS
