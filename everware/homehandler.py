
from tornado import gen
from jupyterhub.handlers.pages import web, BaseHandler
from IPython.html.utils import url_path_join

class HomeHandler(BaseHandler):
    """Render the user's home page."""

    @web.authenticated
    def get(self):
        html = self.render_template('home.html',
            user=self.get_current_user(),
        )
        self.finish(html)

    @gen.coroutine
    def post(self):
        data = {}
        for arg in self.request.arguments:
            data[arg] = self.get_argument(arg)

        repo_url = data['repourl']
        user = self.get_current_user()
        user.last_repo_url = repo_url
        self.db.commit()

        already_running = False
        if user.spawner:
            status = yield user.spawner.poll()
            already_running = (status == None)
        if not already_running:
            yield self.spawn_single_user(user)

        self.redirect(url_path_join(self.hub.server.base_url, user.server.base_url))


