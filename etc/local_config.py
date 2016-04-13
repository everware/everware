# Use this config file to run everware locally on linux or other systems
# that do not need to use a VM to run docker containers

c = get_config()
load_subconfig('etc/base_config.py')
load_subconfig('etc/github_auth.py')
