c = get_config()
load_subconfig('etc/base_config.py')
load_subconfig('etc/github_auth.py')

c.JupyterHub.spawner_class = 'everware.ByorDockerSpawner'

from os.path import join as pjoin
with open(pjoin(c.JupyterHub.template_paths[0], '_byor_options_form.html')) as form:
    c.CustomDockerSpawner.options_form = form.read()
