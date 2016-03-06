import os
import everware


c = get_config()
load_subconfig('base_config.py')

authenticator = everware.GitHubOAuthenticator
c.JupyterHub.authenticator_class = 'everware.GitHubOAuthenticator'
whitelist_file = 'whitelist.txt'
whitelist_handler = everware.DefaultWhitelistHandler(whitelist_file,
                                                     c,
                                                     authenticator)
c.GitHubOAuthenticator.oauth_callback_url = os.environ['OAUTH_CALLBACK_URL']
c.GitHubOAuthenticator.client_id = os.environ['GITHUB_CLIENT_ID']
c.GitHubOAuthenticator.client_secret = os.environ['GITHUB_CLIENT_SECRET']

# change this to the ip that `boot2docker ip` or
# `docker-machine ip <vm_name>`tells you if
# you use boot2docker/a VM, otherwise remove the line
c.Spawner.container_ip = '192.168.99.100'
