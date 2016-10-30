# Test metrica config

c = get_config()
load_subconfig('etc/base_config.py')
load_subconfig('etc/github_auth.py')
c.GAnaliticsIdentificator.g_analitics_id=""