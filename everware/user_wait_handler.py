from tornado import gen, web

from jupyterhub.handlers.pages import BaseHandler
from IPython.html.utils import url_path_join
from tornado.httputil import url_concat
from tornado.escape import json_encode


class UserSpawnHandler(BaseHandler):

    @gen.coroutine
    def get(self, name, user_path):
        current_user = self.get_current_user()
        if current_user and current_user.name == name:
            # logged in, work with spawner
            if current_user.stop_pending:
                self.redirect(url_path_join(self.hub.server.base_url, 'home'))
                return
            is_log_request = self.get_argument('get_logs', False)
            is_failed = False
            is_done = False
            if current_user.spawner:
                log_lines = current_user.spawner.user_log
                is_failed = current_user.spawner.is_failed
                is_running = yield current_user.spawner.is_running()
                if not current_user.spawn_pending and not is_failed and is_running:
                    is_done = True
            else:
                log_lines = []
            if is_log_request:
                resp = {
                    'log': log_lines
                }
                if is_failed:
                    resp.update({
                        'failed': 1
                    })
                elif is_done:
                    resp.update({
                        'done': 1
                    })
                self.finish(json_encode(resp))
            else:
                if is_done:
                    self.set_login_cookie(current_user)
                html = self.render_template(
                    "spawn_pending.html",
                    user=current_user,
                    need_wait=int(is_done)
                )
                self.finish(html)
        else:
            # logged in as a different user, redirect
            target = url_path_join(self.base_url, 'user', current_user.name,
                                   user_path or '')
            self.redirect(target)

