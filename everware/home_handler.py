from tornado import web, gen

from jupyterhub.handlers.base import BaseHandler
from IPython.html.utils import url_path_join
from tornado.httputil import url_concat


class HomeHandler(BaseHandler):
    """Render the user's home page."""

    @web.authenticated
    def get(self):
        user = self.get_current_user()
        repourl = self.get_argument('repourl', '')
        if repourl:
            self.log.info('Got %s in home' % repourl)
            self.redirect(url_concat(
                url_path_join(self.hub.server.base_url, 'spawn'), {
                    'repourl': repourl
                }
            ))
            return
        html = self.render_template('home.html',
            user=user
        )
        self.finish(html)



