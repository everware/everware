c = get_config()
load_subconfig('base_config.py')

c.JupyterHub.authenticator_class = 'dummyauthenticator.DummyAuthenticator'
