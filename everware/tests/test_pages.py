import requests

from jupyterhub.utils import url_path_join as ujoin
from jupyterhub.tests.mocking import public_url, public_host, user_url


def test_root_no_auth(app, io_loop):
    # Test that login page uses GitHub OAuth
    print(app.hub.server.is_up())
    routes = io_loop.run_sync(app.proxy.get_routes)
    print(routes)
    print(app.hub.server)
    url = public_url(app)
    print(url)
    r = requests.get(url)
    r.raise_for_status()
    assert r.url == ujoin(url, app.hub.server.base_url, 'login')
    assert "Sign in with GitHub" in r.text
