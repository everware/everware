import requests

from jupyterhub.tests.conftest import MockHub
from jupyterhub.tests.mocking import public_url

from everware.authenticator import GitHubOAuthenticator
from everware.authenticator import GitHubLoginHandler
from everware.authenticator import GitHubOAuthHandler
from everware.authenticator import WelcomeHandler
from tornado import web



class MockGitHubOAuthHandler(GitHubOAuthHandler):
    def post(self):
        self._mock_username = self.get_argument('username')
        self._mock_password = self.get_argument('password')
        
        username, token = self.authenticator.authenticate(self)

        if username:
            user = self.user_from_username(username)
            user.token = token
            self.set_login_cookie(user)
            user.login_service = "github"
            self.redirect(self.hub.server.base_url)

        else:
            raise web.HTTPError(403)


class MockGitHubOAuthenticator(GitHubOAuthenticator):
    def _admin_users_default(self):
        return {'admin'}

    def authenticate(self, handler):
        # this short circuits any actual auth
        # convention: username == password -> successful login
        #             username != password -> deny login
        # The normal `authenticate` step involves making a request
        # to the OAuth provider who gives us an access token
        # which we then use to lookup the username
        username = handler._mock_username
        password = handler._mock_password
        if username != password:
            return None, None
        
        username = self.normalize_username(username)
        if self.whitelist and username not in self.whitelist:
            return None, None

        return (username, '1234')

    def get_handlers(self, app):
        # replace oauth callback handler with a mock
        # so we can login users without having to contact GitHub
        return [
            (r'/login', WelcomeHandler),
            (r'/oauth_login', GitHubLoginHandler),
            (r'/oauth_callback', MockGitHubOAuthHandler),
        ]


class MockWareHub(MockHub):
    def _authenticator_class_default(self):
        return MockGitHubOAuthenticator

    def login_user(self, name):
        # Works together with MockGitHubOAuthenticator to allow us to
        # login users without having to contact the OAuth provider
        # Need to use POST so we can choose the username which is
        # normally sent by the OAuth provider
        base_url = public_url(self)
        r = requests.post(base_url + 'hub/oauth_callback',
                          data={'username': name,
                                'password': name,
                                },
                          allow_redirects=False,
                          )
        r.raise_for_status()
        assert r.cookies
        return r.cookies
