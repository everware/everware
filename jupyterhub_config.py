import os
import everware


c = get_config()

# spawn with custom docker containers
c.JupyterHub.spawner_class = 'everware.CustomDockerSpawner'
#c.JupyterHub.spawner_class = 'everware.CustomSwarmSpawner'

# The docker instances need access to the Hub, so the default loopback port doesn't work:
# Find it easier to hardcode the IP of the machine it is deployed on
ip_addr = '192.168.99.1'
c.JupyterHub.hub_ip = ip_addr
c.JupyterHub.hub_api_ip = ip_addr

c.JupyterHub.authenticator_class = 'oauthenticator.GitHubOAuthenticator'
c.Authenticator.whitelist = set(['betatim', 'ibab', 'kdungs', 'seneubert', 'alexpearce'])

c.GitHubOAuthenticator.oauth_callback_url = os.environ['OAUTH_CALLBACK_URL']
c.GitHubOAuthenticator.client_id = os.environ['GITHUB_CLIENT_ID']
c.GitHubOAuthenticator.client_secret = os.environ['GITHUB_CLIENT_SECRET']

c.Spawner.tls = True
# Set to False when running docker directly (i.e. on Linux)
#c.Spawner.tls = False
c.Spawner.debug = True
c.Spawner.start_timeout = 180*2
c.Spawner.remove_containers = True
c.Spawner.tls_assert_hostname = False
c.Spawner.use_docker_client_env = True

#c.JupyterHub.data_files_path = 'share'
#c.JupyterHub.template_paths = ['share/static/html']

# change this to the ip that `boot2docker ip` or
# `docker-machine ip <vm_name>`tells you if
# you use boot2docker/a VM, otherwise remove the line
c.Spawner.container_ip = '192.168.99.100'
