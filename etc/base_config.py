# Basic configuration, you should not use this directly
# instead checkout local_config.py or local_dockermacine_config.py


# spawn with custom docker containers
c.JupyterHub.spawner_class = 'everware.CustomDockerSpawner'

c.Spawner.tls = False
c.Spawner.debug = True
c.Spawner.start_timeout = 1000
c.Spawner.remove_containers = True
c.Spawner.tls_assert_hostname = False
c.Spawner.use_docker_client_env = True

# The docker containers need access to the Hub API, so the default
# loopback address doesn't work
from jupyter_client.localinterfaces import public_ips
c.JupyterHub.hub_ip = public_ips()[0]

c.JupyterHub.data_files_path = 'share'
c.JupyterHub.template_paths = ['share/static/html']
