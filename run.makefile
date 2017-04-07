HERE=$(shell pwd)
LOG := everware.log
PIDFILE := everware.pid
EXECUTOR = everware-server

reload:  ## reload everware whitelist
	PID=`pgrep '${EXECUTOR}'` ;\
		if [ -z "$${PID}" ] ; then echo "Cannot find running ${EXECUTOR}" ; exit 1 ; fi
	pkill -1 '${EXECUTOR}'

clean:  ## clean user base
	if [ -f ${PIDFILE} ] ; then echo "${PIDFILE} exists, cannot continute" ; exit 1; fi
	rm -f jupyterhub.sqlite

run-linux: clean  ## run everware server on linux
	source ./env.sh && \
		${EXECUTOR} -f etc/local_config.py --no-ssl 2>&1 | tee ${LOG}

run-dockermachine: clean  ## run everware server on MacOS
	source ./env.sh && \
		${EXECUTOR} -f etc/local_dockermachine_config.py --no-ssl 2>&1 | tee ${LOG}

run-daemon: clean ## run everware in daemon mode, linux only, SSL required
	[ -f ${LOG} ] && mv ${LOG} ${LOG}.`date +%Y%m%d-%s`
	source ./env.sh && \
		${EXECUTOR} -f etc/local_config.py --debug --no-ssl >> ${LOG}  2>&1 &
	pgrep ${EXECUTOR} > ${PIDFILE} || ( tail ${LOG} && rm ${PIDFILE} && exit 1 )
	echo "Started. Log saved to ${LOG}"

stop:
	-rm ${PIDFILE}
	-pkill -9 ${EXECUTOR}
	-pkill -9 node
run-docker-local:
	docker run -d --name everware \
		-v /var/run/docker.sock:/var/run/docker.sock \
		-v ${HERE}/etc/container_config.py:/srv/everware/etc/container_config.py \
		--env-file=env.docker-local \
		-p 8000:8000 \
		-p 8081:8081 \
	everware/everware:latest /srv/everware/etc/container_config.py --no-ssl --debug

run-docker-remote:
	docker run -d --name everware \
		-v ${HERE}/etc/container_config.py:/srv/everware/etc/container_config.py \
		--env-file=env.docker-remote \
		-p 8000:8000 \
		-p 8081:8081 \
	everware/everware:latest /srv/everware/etc/container_config.py --no-ssl --debug

run-docker-swarm:
	docker run -d --name everware \
	      	-v ${HERE}/etc/container_swarm_config.py:/srv/everware/etc/container_swarm_config.py \
     	 	--env-file=env.docker-swarm \
      		-p 8000:8000 \
      		-p 8081:8081 \
      	everware/everware:latest /srv/everware/etc/container_swarm_config.py --no-ssl --debug

stop-docker:
	docker stop everware
	docker rm everware

stop-docker-swarm:
	bash -c "source env.docker-swarm && docker stop everware && docker rm everware"

logs: ${LOG} ## watch log file
	tail -f ${LOG}

