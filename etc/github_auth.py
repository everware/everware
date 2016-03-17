# This adds github based oauth to your everware setup
# You will have to create a OAuth app on github.com
# and store information about it in your environment

import os


c.JupyterHub.authenticator_class = 'everware.GitHubOAuthenticator'
c.GitHubOAuthenticator.oauth_callback_url = os.environ['OAUTH_CALLBACK_URL']
c.GitHubOAuthenticator.client_id = os.environ['GITHUB_CLIENT_ID']
c.GitHubOAuthenticator.client_secret = os.environ['GITHUB_CLIENT_SECRET']
