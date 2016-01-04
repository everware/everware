
from tornado import gen, web

from jupyterhub.handlers.pages import BaseHandler
from IPython.html.utils import url_path_join
import sys


class HomeHandler(BaseHandler):
    """Render the user's home page."""

    @gen.coroutine
    def _spawn_user(self, repo_url):
        print('in _spawn', file=sys.stderr)
        user = self.get_current_user()
        user.last_repo_url = repo_url

        already_running = False
        if user.spawner:
            status = yield user.spawner.poll()
            already_running = (status == None)
        if not already_running:
            yield self.spawn_single_user(user)

        self.redirect(url_path_join(
            self.hub.server.base_url,
            user.server.base_url
        ))

    @web.authenticated
    @gen.coroutine
    def get(self):
        print('in homehandler get', file=sys.stderr)
        repourl_direct = self.get_argument('repourl_direct', '')
        print(self.get_argument('repourl_direct', ''), file=sys.stderr)
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
        print('in HomeHandler post', file=sys.stderr)
        data = {}
        for arg in self.request.arguments:
            data[arg] = self.get_argument(arg)

        repo_url = data['repourl']
        yield self._spawn_user(repo_url)
