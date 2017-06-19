c = get_config()
load_subconfig('etc/base_config.py')
load_subconfig('etc/github_auth.py')

from dockerspawner import DockerSpawner
c.DockerSpawner.hub_ip_connect = c.JupyterHub.hub_ip
