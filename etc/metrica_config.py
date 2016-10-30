# Test metrica config

c = get_config()
load_subconfig('etc/base_config.py')
load_subconfig('etc/github_auth.py')
c.GAnaliticsIdentificator.g_analitics_id="UA-86529451-1"

print(dir(c))
print(c)
print(c.values())