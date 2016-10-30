from traitlets import Unicode
from traitlets.config.configurable import Configurable

class GAnaliticsIdentificator(Configurable) :
	g_analitics_id = Unicode().tag(config=True)
