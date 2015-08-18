import os
import everware

import jupyterhub.handlers.pages
jupyterhub.handlers.pages.HomeHandler.get = everware.HomeHandler.get
jupyterhub.handlers.pages.HomeHandler.post = everware.HomeHandler.post

c = get_config()

# spawn with custom docker containers
c.JupyterHub.spawner_class = 'everware.CustomDockerSpawner'

# The docker instances need access to the Hub, so the default loopback port doesn't work:
from IPython.utils.localinterfaces import public_ips
c.JupyterHub.hub_ip = public_ips()[0]
c.JupyterHub.hub_api_ip = public_ips()[0]

c.JupyterHub.authenticator_class = 'everware.GitHubOAuthenticator'
c.Authenticator.whitelist = set()

c.GitHubOAuthenticator.oauth_callback_url = os.environ['OAUTH_CALLBACK_URL']
c.GitHubOAuthenticator.client_id = os.environ['GITHUB_CLIENT_ID']
c.GitHubOAuthenticator.client_secret = os.environ['GITHUB_CLIENT_SECRET']

c.Spawner.tls = True
c.Spawner.debug = True
c.Spawner.http_timeout = 32
c.Spawner.remove_containers = True
c.Spawner.tls_assert_hostname = False
c.Spawner.use_docker_client_env = True

c.JupyterHub.data_files_path = 'share'
c.JupyterHub.template_paths = ['share/static/html']

# change this to the ip that `boot2docker ip` tells you if
# you use boot2docker, otherwise remove the line
#c.Spawner.container_ip = '192.168.59.103'
