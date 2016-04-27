# Use this config file to run everware in a container,
# and create user containers in local or remote Docker service
#
# In case of local, don't forget to mount /var/run/docker.sock
# In case of remote, don't forget the DOCKER_HOST environment variable

c = get_config()
load_subconfig('etc/base_config.py')
load_subconfig('etc/github_auth.py')

c.JupyterHub.hub_ip = '0.0.0.0'
c.JupyterHub.proxy_api_ip = '0.0.0.0'

# Change these two next settings:
# IP of the machine where the Everware can be contacted
c.DockerSpawner.hub_ip_connect = 'xxx.xxx.xxx.xxx'
# IP of the machine running Docker service
c.DockerSpawner.container_ip = 'xxx.xxx.xxx.xxx'
