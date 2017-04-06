
# Run Everware in a Docker container

This section explains how to run Everware in a container, and the different possibilities to run users container

## Build Everware container

[Dockerfile](Dockerfile)

```
  docker build -t everware .
```

## Create user containers on same machine as the Everware one

Fill the file which will contains environment variables for Everware.
```
  cp env.docker-local.orig env.docker-local
```
Define the `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`, and `OAUTH_CALLBACK_URL`

Edit `etc/container_config.py` file to set `c.DockerSpawner.hub_ip_connect` and `c.DockerSpawner.container_ip` to the IP of your machine running the Everware container.

```
  docker run -d --name everware \
      -v /var/run/docker.sock:/var/run/docker.sock \
      -v $PWD/etc/container_config.py:/srv/everware/etc/container_config.py \
      --env-file=env.docker-local \
      -p 8000:8000 \
      -p 8081:8081 \
      everware /srv/everware/etc/container_config.py --no-ssl --debug
```

Note that you can skip `-v $PWD/etc/container_config.py:/srv/everware/etc/container_config.py` part if you build the container after having modified the config file `etc/container_config.py`

## Create user containers on a remote Docker machine

```
  cp env.docker-remote.orig env.docker-remote
```
Same as before, and define `DOCKER_HOST`, the IP of your remote Docker machine.

```
docker run -d --name everware \
    -v $PWD/etc/container_config.py:/srv/everware/etc/container_config.py \
    --env-file=env.docker-remote \
    -p 8000:8000 \
    -p 8081:8081 \
    everware /srv/everware/etc/container_config.py --no-ssl --debug
```

## Create user containers on a Docker Swarm cluster

This allows to create users container on a Docker Swarm cluster.

```
  cp env.docker-swarm.orig env.docker-swarm
```
Define the variable, and set `DOCKER_HOST` to the IP of your Swarm master.

Edit `etc/container_swarm.py` file to set `c.DockerSpawner.hub_ip_connect` to the IP of your machine hosting Everware container.

```
  docker run --rm -it --name everware \
      -v $PWD/etc/container_swarm_config.py:/srv/everware/etc/container_swarm_config.py \
      -v /home/ubuntu/docker:/etc/docker \
      --env-file=env.docker-swarm \
      -p 8000:8000 \
      -p 8081:8081 \
      everware /srv/everware/etc/container_swarm_config.py --no-ssl --debug
```
