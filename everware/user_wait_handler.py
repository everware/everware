from tornado import gen, web

from jupyterhub.handlers.pages import BaseHandler
from IPython.html.utils import url_path_join
from tornado.httputil import url_concat
from tornado.escape import json_encode
from . import __version__
from .metrica import MetricaIdsMixin

class UserSpawnHandler(BaseHandler):

    @gen.coroutine
    def get(self, name, user_path):
        current_user = self.get_current_user()
        if current_user and current_user.name == name:
            # logged in, work with spawner
            is_log_request = self.get_argument('get_logs', False)
            is_failed = False
            is_up = False
            if current_user.spawner:
                spawner = current_user.spawner
                is_running = yield spawner.is_running()
                log_lines = spawner.user_log
                is_failed = spawner.is_failed
                is_up = spawner.is_up
                if spawner.is_empty and not is_failed:
                    self.redirect(url_path_join(self.hub.server.base_url, 'home'))
                    return
            else:
                log_lines = []
            if current_user.stop_pending and not is_failed:
                self.redirect(url_path_join(self.hub.server.base_url, 'home'))
                return
            if is_log_request:
                resp = {
                    'log': log_lines
                }
                if is_failed:
                    resp.update({
                        'failed': 1
                    })
                elif is_up:
                    resp.update({
                        'done': 1
                    })
                self.finish(json_encode(resp))
            else:
                if is_up:
                    self.set_login_cookie(current_user)
                    target = '/user/%s' % (
                        current_user.name
                    )
                    self.log.info('redirecting to %s' % target)
                    self.redirect(target)
                    return
                metrica = MetricaIdsMixin()
                g_id = metrica.g_analitics_id
                ya_id = metrica.ya_metrica_id
                html = self.render_template(
                    "spawn_pending.html",
                    version=__version__,
                    g_analitics_id=g_id,
                    ya_metrica_id=ya_id
                )
                self.finish(html)
        else:
            # logged in as a different user, redirect
            target = url_path_join(self.base_url, 'login')
            self.redirect(target)

