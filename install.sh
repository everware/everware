#!/bin/bash

halt() {
echo $* 
exit 1
}

npm install
npm install -g configurable-http-proxy
PYTHON_MAJOR=`python -c 'import sys; print(sys.version_info[0])'`

if [ $PYTHON_MAJOR -eq 3 ] ; then
  PYTHON=python
  PIP=pip
elif [ -n `which python3` ] ; then
  PYTHON=python3
  PIP=pip3
fi

[ -n $PYTHON ] || halt "Cannot find python3"

$PIP install -e .
$PYTHON setup.py css
$PYTHON setup.py js

cp env.sh.orig env.sh
cp jupyterhub_config.py.orig jupyterhub_config.py

echo "Modify 'env.sh' and 'jupyterhub_config.py' and then"
echo "./run.sh"
