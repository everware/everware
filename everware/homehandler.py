
from tornado import gen, web

from jupyterhub.handlers.pages import BaseHandler
from IPython.html.utils import url_path_join
from urllib.parse import urlencode


class HomeHandler(BaseHandler):
    """Render the user's home page."""

    @gen.coroutine
    def _spawn_user(self, repo_url):
        user = self.get_current_user()
        try:
            user.last_repo_url = repo_url
            self.redirect(url_path_join(
                self.hub.server.base_url,
                user.server.base_url
            ))
        except AttributeError:
            # user's server hasn't been created
            query = {
                'repo_url': repo_url
            }
            self.redirect(url_path_join(
                self.hub.server.base_url,
                'user',
                user.escaped_name + '?' + urlencode(query)
            ))

    @web.authenticated
    @gen.coroutine
    def get(self):
        repourl_direct = self.get_argument('repourl_direct', '')
        if repourl_direct:
            yield self._spawn_user(repourl_direct)
        else:
            html = self.render_template(
                'home.html',
                user=self.get_current_user(),
                repo_url=self.get_argument('repo_url', ''),
            )
            self.finish(html)

    @web.authenticated
    @gen.coroutine
    def post(self):
        data = {}
        for arg in self.request.arguments:
            data[arg] = self.get_argument(arg)

        repo_url = data['repourl']
        yield self._spawn_user(repo_url)
