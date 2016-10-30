from traitlets import Unicode
from traitlets.config import ConfigurableSingleton

class GAnaliticsIdentificator(ConfigurableSingleton) :

	g_analitics_id = Unicode('', help='''
		Google Analitics uniq id.
		''', config=True)
