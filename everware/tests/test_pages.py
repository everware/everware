import requests

from jupyterhub.utils import url_path_join as ujoin
from jupyterhub.tests.mocking import public_url, public_host, user_url


def test_github_login_no_auth(app, io_loop):
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

def test_authed_user_bypasses_login(app):
    # A logged in user should go straight to the control panel
    cookies = app.login_user('river')
    r = requests.get(public_url(app), cookies=cookies)
    r.raise_for_status()
    url = public_url(app)
    print(url)
    print(app.hub.server.base_url)
    assert r.url == ujoin(url, app.hub.server.base_url, 'home')

def test_username_case(app):
    # A logged in user should go straight to the control panel
    cookies = app.login_user('River')
    r = requests.get(public_url(app), cookies=cookies)
    r.raise_for_status()
    assert 'Logged in as river' in r.text

def test_whitelist(app):
    url = public_url(app)
    r = requests.post(
        ujoin(url, app.hub.server.base_url, 'oauth_callback'),
        data={
            'username': 'wrong',
            'password': 'wrong'
        }
    )
    assert r.status_code == 403
    text = ('Your username is not whitelisted on this server. '
            'Please contact the system administrator.')
    assert text in r.text
