# Makefile for building & starting rep-containers
# arguments can be supplied by -e definitions:
#
#    TESTS -- list of tests to run
#    M -- commit message
#
#

SHELL := /bin/bash
TEST_OPTIONS := -s tests -N 2
TESTS := test_happy_mp
LOG := everware.log
PIDFILE := everware.pid
IP ?= $(shell python -c 'from IPython.utils.localinterfaces import public_ips; print (public_ips()[0])' 2>/dev/null)
OPTIONS = --debug --port 8000 --no-ssl --JupyterHub.hub_ip=$${IP}
IS_DOCKER_MACHINE := $(shell which docker-machine > /dev/null ; echo $$?)
UPLOADDIR ?= ~/upload_screens
PYTHON_MAJOR = $(shell python -c 'import sys; print(sys.version_info[0])')
IS_PYTHON3 = $(shell which python3)

ifeq (${PYTHON_MAJOR}, 3)
	PYTHON = python
	PIP = pip
else ifdef IS_PYTHON3
	PYTHON = python3
	PIP = pip3
else
	$(error Unable to find python)
endif

EXECUTOR = everware-server

ifeq (0, $(IS_DOCKER_MACHINE))
	SPAWNER_IP = "192.168.99.100"
else
	SPAWNER_IP = "127.0.0.1"
endif

.PHONY: install reload clean run run-daemon run-test stop test-client tail

help:
	@echo Usage: make [-e VARIABLE=VALUE] targets
	@echo "variables:"
	@grep -h "#\s\+\w\+ -- " $(MAKEFILE_LIST) |sed "s/#\s//"
	@echo
	@echo targets and corresponding dependencies:
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' -e 's/^/   /' | sed -e 's/##//'


install:  ## install everware
	npm install
	npm install configurable-http-proxy
	${PIP} install $${PIP_OPTIONS} -r requirements.txt && \
	${PIP} install -e . && \
	${PYTHON} setup.py css && \
	${PYTHON} setup.py js

	if [ ! -f env.sh ] ; then cp env.sh.orig env.sh ; fi
	if [ ! -f jupyterhub_config.py ] ; then cp jupyterhub_config.py.orig jupyterhub_config.py ; fi
	if [ ! -f whitelist.txt ] ; then cp whitelist.txt.orig whitelist.txt ; fi

reload:  ## reload everware whitelist
	PID=`pgrep -f -n '${EXECUTOR}'` ;\
		if [ -z "$${PID}" ] ; then echo "Cannot find ${PIDFILE}" ; exit 1 ; fi
	pkill -1 -f -n '${EXECUTOR}'

clean:  ## clean user base
	if [ -f ${PIDFILE} ] ; then echo "${PIDFILE} exists, cannot continute" ; exit 1; fi
	rm -f jupyterhub.sqlite

run: clean  ## run everware server
	source ./env.sh && \
		${EXECUTOR} ${OPTIONS}

run-daemon: clean
	source ./env.sh && \
		${EXECUTOR} ${OPTIONS} >> ${LOG}  2> /dev/null &
	pgrep -f ${EXECUTOR} > ${PIDFILE} || ( tail ${LOG} && exit 1 )
	echo "Started. Log saved to ${LOG}"

stop: ${PIDFILE}
	rm ${PIDFILE}
	kill -9 `cat ${PIDFILE}` || pkill -9 -f configurable-http-proxy

stop-zombie:
	pkill -9 -f jupyterhub || pkill -9 -f configurable-http-proxy

run-test-server:  clean ## run everware instance for testing (no auth)
	cat jupyterhub_config.py <(echo c.JupyterHub.authenticator_class = 'dummyauthenticator.DummyAuthenticator') \
		<(echo c.Spawner.container_ip = \'${SPAWNER_IP}\') \
		> jupyterhub_config_test.py
	source ./env.sh && \
		export EVERWARE_WHITELIST= ; \
		${EXECUTOR} ${OPTIONS} --JupyterHub.config_file=jupyterhub_config_test.py >& ${LOG} &
	@sleep 1
	pgrep -f '${EXECUTOR}' > ${PIDFILE} || exit 1
	echo "Started. Log saved to ${LOG}"

logs: ${LOG} ## watch log file
	tail -f ${LOG}

test: ## run tests
	export UPLOADDIR=${UPLOADDIR} && build_tools/test_frontend.sh

test-client: ## run tests
	export UPLOADDIR=${UPLOADDIR} ; \
		nose2 ${TEST_OPTIONS} ${TESTS}

gistup: ## install gistup
	git clone https://github.com/anaderi/gistup.git src/gistup
	cd src/gistup ; \
		npm install -g

upload_screens: ## upload screenshots of failed tests
	@which gistup > /dev/null || (echo "setup https://github.com/anaderi/gistup first" && exit 1 )
	echo ${UPLOADDIR}
	if [[ `find ${UPLOADDIR} -not -path "*/.git/*" -type f -print` != "" ]] ; then \
		cd ${UPLOADDIR} ; \
		if [ ! -d ".git" ] ; then \
			if [[ ! -f ~/.gistup.json  ]] ; then \
				if [ -n "$${GIST_TOKEN}" ] ; then \
					echo "{\"token\": \"$${GIST_TOKEN}\", \"protocol\": \"https\" }" > ~/.gistup.json ; \
				else \
					echo "no GIST_TOKEN specified. exit"; exit 1; \
				fi ; \
			fi ;\
			OPTIONS="--no-open" ; \
			if [ "${M}" != "" ] ; then OPTIONS+=" --description '${M}'" ; fi ;\
			gistup $${OPTIONS} ; \
		else \
			git add * ;\
			git commit -am "${M}" ;\
			git push ;\
		fi ;\
	fi

