c = get_config()
load_subconfig('etc/base_config.py')

c.JupyterHub.authenticator_class = 'dummyauthenticator.DummyAuthenticator'
c.Spawner.start_timeout = 30
