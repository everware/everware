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
IP = $(shell python -c 'from IPython.utils.localinterfaces import public_ips; print (public_ips()[0])' 2>/dev/null)
OPTIONS = --debug --port 8000 --no-ssl --JupyterHub.hub_ip=${IP}
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

ifeq ($(shell uname -s),Linux)
	SPAWNER_IP = "127.0.0.1"
else
	SPAWNER_IP = "192.168.99.100"
endif

include run.makefile

.PHONY: install reload clean run run-daemon stop test tail

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
	${PIP} install $${PIP_OPTIONS} -r requirements.txt
	${PIP} install -e .
	${PYTHON} setup.py css
	${PYTHON} setup.py js

	if [ ! -f env.sh ] ; then cp env.sh.orig env.sh ; fi

docker-build: ## build docker image
	docker build --no-cache -t everware/everware:0.10.0 .

test: ## run all tests
	export UPLOADDIR=${UPLOADDIR}; \
		py.test everware/ && \
		build_tools/test_frontend.sh --Spawner.container_ip=${SPAWNER_IP}

gistup: ## install gistup
	git clone https://github.com/anaderi/gistup.git src/gistup
	cd src/gistup ; \
		npm install -g

upload_screens: ## upload screenshots of failed tests
	@which gistup > /dev/null || (echo "setup https://github.com/anaderi/gistup first" && exit 1 )
	echo ${UPLOADDIR}
	if [[ -d ${UPLOADDIR} && `find ${UPLOADDIR} -not -path "*/.git/*" -type f -print` != "" ]] ; then \
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
