# Test metrica config

c = get_config()
load_subconfig('etc/base_config.py')
load_subconfig('etc/github_auth.py')
c.MetricaIdsMixin.g_analitics_id=""
c.MetricaIdsMixin.ya_metrica_id=""