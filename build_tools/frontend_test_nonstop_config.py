c = get_config()
load_subconfig('build_tools/frontend_test_normal_config.py')
c.Spawner.remove_containers = False
