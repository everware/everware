# Use this config file to run everware in a container,
# and create the user container on a Docker Swarm cluster
#
# No need to mount /var/run/docker.sock,
# but don't forget to set Docker Swarm environment
# variables in the env file

import os

c = get_config()
load_subconfig('etc/base_config.py')
load_subconfig('etc/github_auth.py')

c.JupyterHub.hub_ip = '0.0.0.0'
c.JupyterHub.proxy_api_ip = '0.0.0.0'

c.JupyterHub.spawner_class = 'everware.CustomSwarmSpawner'
c.Spawner.tls = True
c.DockerSpawner.tls = True

# Change this setting:
# IP of the machine where the Everware can be contacted
c.DockerSpawner.hub_ip_connect = os.environ['DOCKER_PUBLIC_IP']
