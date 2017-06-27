c = get_config()
load_subconfig('etc/base_config.py')
load_subconfig('etc/github_auth.py')

c.JupyterHub.spawner_class = 'everware.ByorDockerSpawner'
