# Use this config file to run everware locally on Mac OS or Windows

c = get_config()
load_subconfig('etc/base_config.py')
load_subconfig('etc/github_auth.py')

# change this to the ip that `boot2docker ip` or
# `docker-machine ip <vm_name>`tells you. If you are not using `docker-machine`
# or `boot2docker` you do not need to load this config file
c.Spawner.container_ip = '192.168.99.100'
