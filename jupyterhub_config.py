import os
import everware

import jupyterhub.handlers.pages
import signal

jupyterhub.handlers.pages.HomeHandler.get = everware.HomeHandler.get
jupyterhub.handlers.pages.HomeHandler.post = everware.HomeHandler.post
jupyterhub.handlers.pages.HomeHandler._spawn_user = everware.HomeHandler._spawn_user

c = get_config()

# spawn with custom docker containers
c.JupyterHub.spawner_class = 'everware.CustomDockerSpawner'
# c.JupyterHub.spawner_class = 'everware.CustomSwarmSpawner'

# The docker instances need access to the Hub, so the default loopback port doesn't work:
# Find it easier to hardcode the IP of the machine it is deployed on
# from IPython.utils.localinterfaces import public_ips
c.JupyterHub.hub_ip = '172.17.0.1'  # public_ips()[0]
c.JupyterHub.hub_api_ip = '172.17.0.1'  # public_ips()[0]

authenticator = everware.GitHubOAuthenticator


def set_whitelist(signal, frame):
    whitelist = set(x.rstrip() for x in open('whitelist'))
    if not signal:
        c.Authenticator.whitelist = whitelist
    else:
        authenticator.whitelist = whitelist

c.JupyterHub.authenticator_class = 'everware.%s' % authenticator.__name__
signal.signal(signal.SIGHUP, set_whitelist)
set_whitelist(None, None)

c.GitHubOAuthenticator.oauth_callback_url = os.environ['OAUTH_CALLBACK_URL']
c.GitHubOAuthenticator.client_id = os.environ['GITHUB_CLIENT_ID']
c.GitHubOAuthenticator.client_secret = os.environ['GITHUB_CLIENT_SECRET']

c.Spawner.tls = True
# Set to False when running docker directly (i.e. on Linux)
# c.Spawner.tls = False
c.Spawner.debug = True
c.Spawner.start_timeout = 180 * 2
c.Spawner.remove_containers = True
c.Spawner.tls_assert_hostname = False
c.Spawner.use_docker_client_env = True

c.JupyterHub.data_files_path = 'share'
c.JupyterHub.template_paths = ['share/static/html']

# change this to the ip that `boot2docker ip` tells you if
# you use boot2docker, otherwise remove the line
#c.Spawner.container_ip = '192.168.59.103'
