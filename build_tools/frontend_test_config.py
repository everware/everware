c = get_config()
load_subconfig('etc/base_config.py')

c.JupyterHub.authenticator_class = 'dummyauthenticator.DummyAuthenticator'
c.Spawner.start_timeout = 50
c.Spawner.http_timeout = 45 # docker sometimes doesn't show up for a while
