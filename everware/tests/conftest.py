from jupyterhub.tests.conftest import *
from .mocking import MockWareHub


@fixture(scope='module')
def app(request):
    app = MockWareHub.instance(log_level=logging.DEBUG)
    app.start(['-f', 'everware/tests/mock_config.py'])
    def fin():
        MockWareHub.clear_instance()
        app.stop()
    request.addfinalizer(fin)
    return app

