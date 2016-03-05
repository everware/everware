# Makefile for building & starting rep-containers
# arguments can be supplied by -e definitions: 
#
#    TESTS -- list of tests to run
#
#

SHELL := /bin/bash
OPTIONS := --debug --port 8000 --log-file=jupyterhub.log --no-ssl
TEST_OPTIONS := -s tests -N 2
TESTS := case_happy_mp

.PHONY: install reload clean run


help:
	@echo Usage: make [-e VARIABLE=VALUE] targets
	@echo "variables:"
	@grep -h "#\s\+\w\+ -- " $(MAKEFILE_LIST) |sed "s/#\s//"
	@echo
	@echo targets and corresponding dependencies:
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' -e 's/^/   /' | sed -e 's/##//'


install:  ## install everware
	npm install
	npm install -g configurable-http-proxy
	PYTHON_MAJOR=`python -c 'import sys; print(sys.version_info[0])'` ;\
		if [ $${PYTHON_MAJOR} -eq 3 ] ; then \
			PYTHON=python ;\
			PIP=pip ;\
		elif [ -n `which python3` ] ; then \
			PYTHON=python3 ;\
			PIP=pip3 ;\
		else \
			echo "Unable to find python" ;\
			exit 1 ;\
		fi ;\
		$${PIP} install -e . ;\
		$${PYTHON} setup.py css ;\
		$${PYTHON} setup.py js ;\

	if [ ! -f env.sh ] ; then cp env.sh.orig env.sh ; fi
	if [ ! -f jupyterhub_config.py ] ; then cp jupyterhub_config.py.orig jupyterhub_config.py ; fi
	if [ ! -f whitelist.txt ] ; then cp whitelist.txt.orig whitelist.txt ; fi

reload:  ## reload everware whitelist
	PID=`pgrep -f jupyterhub` ;\
		if [ -z $${PID} ] ; then echo "Cannot find jupyterhub running" ; exit 1 ; fi
	pkill -1 -f jupyterhub

clean:  ## clean user base
	rm -f jupyterhub.sqlite

run: clean  ## run everware server
	source ./env.sh && \
		jupyterhub ${OPTIONS}

run-test:  clean ## run everware instance for testing (no auth)
	cat jupyterhub_config.py <(echo c.JupyterHub.authenticator_class = 'dummyauthenticator.DummyAuthenticator') > jupyterhub_config_test.py
	source ./env.sh && \
		jupyterhub ${OPTIONS} --config=jupyterhub_config_test.py

test-client: ## run selenium tests
	nose2 ${TEST_OPTIONS} ${TESTS}
