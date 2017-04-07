# Use this config file to run everware in a container,
# and create user containers in local or remote Docker service
#
# In case of local, don't forget to mount /var/run/docker.sock
# In case of remote, don't forget the DOCKER_HOST environment variable

import os

c = get_config()
load_subconfig('etc/base_config.py')
load_subconfig('etc/github_auth.py')

c.JupyterHub.hub_ip = '0.0.0.0'
c.JupyterHub.proxy_api_ip = '0.0.0.0'

# IP of the machine where the Everware (run as docker container) can be contacted
c.DockerSpawner.hub_ip_connect = os.environ['DOCKER_PUBLIC_IP']
# IP of the machine running Docker service, normally the same as above
c.DockerSpawner.container_ip = c.DockerSpawner.hub_ip_connect
