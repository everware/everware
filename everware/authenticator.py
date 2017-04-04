"""
Custom Authenticator to use GitHub OAuth with JupyterHub

Most of the code c/o Kyle Kelley (@rgbkrk)
"""

import json
import os
import urllib
import signal

from tornado.auth import OAuth2Mixin
from tornado.escape import url_escape
from tornado import gen, web

from tornado.httputil import url_concat
from tornado.httpclient import HTTPRequest, AsyncHTTPClient

from jupyterhub.handlers import BaseHandler
from jupyterhub.auth import Authenticator, LocalAuthenticator
from jupyterhub.utils import url_path_join

from traitlets import Unicode, Set
from traitlets.config import LoggingConfigurable
from . import __version__


class DefaultWhitelistHandler(LoggingConfigurable):
    def __init__(self, filename, config, authenticator):
        super().__init__()
        self.filename = filename
        self.authenticator = authenticator
        if os.path.exists(filename):
            whitelist = set(x.rstrip() for x in open(filename))
            self.log.info('Found whitelist %s' % filename)
            self.log.info('Logins:\n' + '\n'.join('\t%s' % cur_name for cur_name in whitelist))
        else:
            whitelist = set()
            self.log.warn("Whitelist %s wasn't found" % filename)
        config.Authenticator.whitelist = whitelist
        signal.signal(signal.SIGHUP, self.reload_whitelist)

    def reload_whitelist(self, signal, frame):
        if os.path.exists(self.filename):
            self.authenticator.whitelist = set(
                x.rstrip() for x in open(self.filename)
            )
            self.log.info(
                'Whitelist reloaded:\n%s',
                '\n'.join(self.authenticator.whitelist)
            )
        else:
            self.log.warn("whitelist file (%s) not found" % self.filename)


class GitHubMixin(OAuth2Mixin):
    _OAUTH_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
    _OAUTH_ACCESS_TOKEN_URL = "https://github.com/login/oauth/access_token"


class BitbucketMixin(OAuth2Mixin):
    _OAUTH_AUTHORIZE_URL = "https://bitbucket.org/site/oauth2/authorize"
    _OAUTH_ACCESS_TOKEN_URL = "https://bitbucket.org/site/oauth2/access_token"


class WelcomeHandler(BaseHandler):
    """Render the login page."""

    def _render(self, login_error=None, username=None):
        return self.render_template('login.html',
                                    next=url_escape(self.get_argument('next', default='')),
                                    repourl=url_escape(self.get_argument('repourl', default='')),
                                    username=username,
                                    login_error=login_error,
                                    version=__version__
                                    )

    def get(self):
        next_url = self.get_argument('next', '')

        if not next_url.startswith('/'):
            # disallow non-absolute next URLs (e.g. full URLs)
            next_url = ''
        user = self.get_current_user()
        if user:
            if not next_url:
                if user.running:
                    next_url = user.server.base_url
                else:
                    next_url = self.hub.server.base_url
            # set new login cookie
            # because single-user cookie may have been cleared or incorrect
            # self.set_login_cookie(self.get_current_user())
            self.redirect('/oauth_login', permanent=False)
        else:
            self.finish(self._render())


class OAuthLoginHandler(BaseHandler):
    def get(self):
        guess_uri = '{proto}://{host}{path}'.format(
            proto=self.request.protocol,
            host=self.request.host,
            path=url_path_join(
                self.hub.server.base_url,
                'oauth_callback'
            )
        )

        redirect_uri = self.authenticator.oauth_callback_url or guess_uri
        self.log.info('oauth redirect: %r', redirect_uri)

        repourl = self.get_argument('repourl', '')

        state = {'unique': 42}
        if repourl:
            state['repourl'] = repourl
        state.update({param: self.get_argument(param) for param in self.request.arguments})

        self.authorize_redirect(
            redirect_uri=redirect_uri,
            client_id=self.authenticator.client_id,
            scope=['repo'],
            response_type='code',
            extra_params={'state': self.create_signed_value('state', repr(state))})


class GitHubLoginHandler(OAuthLoginHandler, GitHubMixin):
    pass


class BitbucketLoginHandler(OAuthLoginHandler, BitbucketMixin):
    pass


class GitHubOAuthHandler(BaseHandler):
    @gen.coroutine
    def get(self):
        # Check state argument, should be there and contain a dict
        # as created in OAuthLoginHandler
        state = self.get_secure_cookie('state', self.get_argument('state', ''))
        if state is None:
            raise web.HTTPError(403)

        state = eval(state)
        self.log.debug('State dict: %s', state)
        state.pop('unique')

        username, token = yield self.authenticator.authenticate(self)
        if username:
            user = self.user_from_username(username)
            user.token = token
            self.set_login_cookie(user)
            user.login_service = "github"
            if 'repourl' in state:
                self.log.debug("Redirect with %s", state)
                self.redirect(self.hub.server.base_url + '/home?' + urllib.parse.urlencode(state))
            else:
                self.redirect(self.hub.server.base_url + '/home')
        else:
            raise web.HTTPError(403)


class BitbucketOAuthHandler(GitHubOAuthHandler):
    pass


class GitHubOAuthenticator(Authenticator):
    login_service = "GitHub"
    oauth_callback_url = Unicode('', config=True)
    client_id = Unicode(os.environ.get('GITHUB_CLIENT_ID', ''),
                        config=True)
    client_secret = Unicode(os.environ.get('GITHUB_CLIENT_SECRET', ''),
                            config=True)

    def login_url(self, base_url):
        return url_path_join(base_url, 'login')

    def get_handlers(self, app):
        return [
            (r'/login', WelcomeHandler),
            (r'/oauth_login', GitHubLoginHandler),
            (r'/oauth_callback', GitHubOAuthHandler),
        ]

    @gen.coroutine
    def authenticate(self, handler):
        code = handler.get_argument("code", False)
        if not code:
            raise web.HTTPError(400, "oauth callback made without a token")
        # TODO: Configure the curl_httpclient for tornado
        http_client = AsyncHTTPClient()

        # Exchange the OAuth code for a GitHub Access Token
        #
        # See: https://developer.github.com/v3/oauth/

        # GitHub specifies a POST request yet requires URL parameters
        params = dict(
            client_id=self.client_id,
            client_secret=self.client_secret,
            code=code
        )

        url = url_concat("https://github.com/login/oauth/access_token",
                         params)

        req = HTTPRequest(url,
                          method="POST",
                          headers={"Accept": "application/json"},
                          body=''  # Body is required for a POST...
                          )

        resp = yield http_client.fetch(req)
        resp_json = json.loads(resp.body.decode('utf8', 'replace'))

        access_token = resp_json['access_token']

        # Determine who the logged in user is
        headers = {"Accept": "application/json",
                   "User-Agent": "JupyterHub",
                   "Authorization": "token {}".format(access_token)
                   }
        req = HTTPRequest("https://api.github.com/user",
                          method="GET",
                          headers=headers
                          )
        resp = yield http_client.fetch(req)
        resp_json = json.loads(resp.body.decode('utf8', 'replace'))

        username = self.normalize_username(resp_json["login"])
        if self.whitelist and username not in self.whitelist:
            username = None
        raise gen.Return((username, access_token))


class BitbucketOAuthenticator(Authenticator):
    login_service = "Bitbucket"
    oauth_callback_url = Unicode(os.environ.get('OAUTH_CALLBACK_URL', ''),
                                 config=True)
    client_id = Unicode(os.environ.get('BITBUCKET_CLIENT_ID', ''),
                        config=True)
    client_secret = Unicode(os.environ.get('BITBUCKET_CLIENT_SECRET', ''),
                            config=True)
    team_whitelist = Set(
        config=True,
        help="Automatically whitelist members of selected teams",
    )

    def login_url(self, base_url):
        return url_path_join(base_url, 'oauth_login')

    def get_handlers(self, app):
        return [
            (r'/oauth_login', BitbucketLoginHandler),
            (r'/oauth_callback', BitbucketOAuthHandler),
        ]

    @gen.coroutine
    def authenticate(self, handler):
        code = handler.get_argument("code", False)
        if not code:
            raise web.HTTPError(400, "oauth callback made without a token")
        # TODO: Configure the curl_httpclient for tornado
        http_client = AsyncHTTPClient()

        params = dict(
            client_id=self.client_id,
            client_secret=self.client_secret,
            grant_type="authorization_code",
            code=code,
            redirect_uri=self.oauth_callback_url
        )

        url = url_concat(
            "https://bitbucket.org/site/oauth2/access_token", params)
        self.log.info(url)

        bb_header = {"Content-Type":
                         "application/x-www-form-urlencoded;charset=utf-8"}
        req = HTTPRequest(url,
                          method="POST",
                          auth_username=self.client_id,
                          auth_password=self.client_secret,
                          body=urllib.parse.urlencode(params).encode('utf-8'),
                          headers=bb_header
                          )

        resp = yield http_client.fetch(req)
        resp_json = json.loads(resp.body.decode('utf8', 'replace'))

        access_token = resp_json['access_token']

        # Determine who the logged in user is
        headers = {"Accept": "application/json",
                   "User-Agent": "JupyterHub",
                   "Authorization": "Bearer {}".format(access_token)
                   }
        req = HTTPRequest("https://api.bitbucket.org/2.0/user",
                          method="GET",
                          headers=headers
                          )
        resp = yield http_client.fetch(req)
        resp_json = json.loads(resp.body.decode('utf8', 'replace'))

        username = self.normalize_username(resp_json["username"])
        whitelisted = yield self.check_whitelist(username, headers)
        if not whitelisted:
            username = None
        return username

    def check_whitelist(self, username, headers):
        if self.team_whitelist:
            return self._check_group_whitelist(username, headers)
        else:
            return self._check_user_whitelist(username)

    @gen.coroutine
    def _check_user_whitelist(self, user):
        return (not self.whitelist) or (user in self.whitelist)

    @gen.coroutine
    def _check_group_whitelist(self, username, headers):
        http_client = AsyncHTTPClient()

        # We verify the team membership by calling teams endpoint.
        # Re-use the headers, change the request.
        next_page = url_concat("https://api.bitbucket.org/2.0/teams",
                               {'role': 'member'})
        user_teams = set()
        while next_page:
            req = HTTPRequest(next_page, method="GET", headers=headers)
            resp = yield http_client.fetch(req)
            resp_json = json.loads(resp.body.decode('utf8', 'replace'))
            next_page = resp_json.get('next', None)

            user_teams |= \
                set([entry["username"] for entry in resp_json["values"]])
        return len(self.team_whitelist & user_teams) > 0


class LocalGitHubOAuthenticator(LocalAuthenticator, GitHubOAuthenticator):
    """A version that mixes in local system user creation"""
    pass


class LocalBitbucketOAuthenticator(LocalAuthenticator,
                                   BitbucketOAuthenticator):
    """A version that mixes in local system user creation"""
    pass

class DummyTokenAuthenticator(Authenticator):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.test_token = None

    @gen.coroutine
    def authenticate(self, handler, data):
        self.test_token = data['password']
        return data['username']