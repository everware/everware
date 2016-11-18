from traitlets import Unicode
from traitlets.config import Configurable, get_config

class MetricaIdsMixin(Configurable) :

	g_analitics_id = Unicode('', help='''
		Google Analitics uniq id.
		''').tag(config=True)

	ya_metrica_id = Unicode('', help='''
		Yandex Metrica uniq id.
		''').tag(config=True)


	def __init__(self, config=None):
		super(MetricaIdsMixin, self).__init__(config=get_config())