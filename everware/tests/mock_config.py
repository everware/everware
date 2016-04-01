import os
import everware
import everware.tests.mocking

c = get_config()

c.JupyterHub.data_files_path = 'share'
c.JupyterHub.template_paths = ['share/static/html']
c.Authenticator.whitelist = set(['river'])
