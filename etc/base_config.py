import os
import everware
import jupyterhub.handlers.pages
import jupyterhub.handlers.base


# TODO: find a way to change default handlers
# instead of this shit
jupyterhub.handlers.base.UserSpawnHandler.get = everware.UserSpawnHandler.get
jupyterhub.handlers.pages.SpawnHandler.post = everware.SpawnHandler.post
jupyterhub.handlers.pages.SpawnHandler.get = everware.SpawnHandler.get
jupyterhub.handlers.pages.SpawnHandler._spawn = everware.SpawnHandler._spawn
jupyterhub.handlers.pages.HomeHandler.get = everware.HomeHandler.get

c = get_config()

# spawn with custom docker containers
c.JupyterHub.spawner_class = 'everware.CustomDockerSpawner'

c.Spawner.tls = False
c.Spawner.debug = True
c.Spawner.start_timeout = 1000
c.Spawner.remove_containers = True
c.Spawner.tls_assert_hostname = False
c.Spawner.use_docker_client_env = True

# The docker containers need access to the Hub API, so the default
# loopback address doesn't work
from jupyter_client.localinterfaces import public_ips
c.JupyterHub.hub_ip = public_ips()[0]

c.JupyterHub.data_files_path = 'share'
c.JupyterHub.template_paths = ['share/static/html']
