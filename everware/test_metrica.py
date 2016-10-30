from traitlets import Unicode
from traitlets.config import Configurable, get_config

class GAnaliticsIdentificator(Configurable) :

	g_analitics_id = Unicode('', help='''
		Google Analitics uniq id.
		''', config=True)

	def __init__(self, config=None):
		super(GAnaliticsIdentificator, self).__init__(config=get_config())