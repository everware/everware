from tornado import gen, web

from jupyterhub.handlers.pages import BaseHandler
from IPython.html.utils import url_path_join
from tornado.httputil import url_concat
from tornado.escape import json_encode


class UserSpawnHandler(BaseHandler):
    """Requests to /user/name handled by the Hub
    should result in spawning the single-user server and
    being redirected to the original.
    """

    @gen.coroutine
    def get(self, name):
        current_user = self.get_current_user()
        repo_url = self.get_argument('repo_url', '')
        if repo_url:
            current_user.last_repo_url = repo_url
        is_log_request = self.get_argument('get_logs', False)
        is_failed = False
        if current_user and current_user.name == name:
            # logged in, work with spawner
            if current_user.spawner:
                log_lines = current_user.spawner.user_log
                is_failed = current_user.spawner.is_failed
                if not current_user.spawn_pending and not is_failed:
                    # user's server has started or
                    # even hasn't been created
                    is_running = yield current_user.spawner.is_running()
                    if is_running and is_log_request:
                        self.finish(json_encode({
                            'log': log_lines,
                            'done': 1
                        }))
                        return
                    if is_running:
                        # set login cookie anew
                        self.set_login_cookie(current_user)
                        without_prefix = self.request.uri[
                            len(self.hub.server.base_url):
                        ]
                        target = url_path_join(self.base_url, without_prefix)

                        params_start = target.find('?')
                        if params_start != -1:
                            target = target[:params_start]
                        self.log.debug('go to %s', target)
                        self.redirect(target)
                        return
            else:
                log_lines = []

            if is_log_request:
                resp = {
                    'log': log_lines
                }
                if is_failed:
                    resp.update({
                        'stop': 1
                    })
                self.finish(json_encode(resp))
            else:
                html = self.render_template(
                    "spawn_pending.html",
                    user=current_user,
                )
                self.finish(html)
                if is_failed:
                    return
                if not current_user.spawner:
                    yield self.spawn_single_user(current_user)
                elif not current_user.spawn_pending and not is_running:
                    yield self.spawn_single_user(current_user)
        else:
            # not logged in to the right user,
            # clear any cookies and reload (will redirect to login)
            self.clear_login_cookie()
            self.redirect(url_concat(
                self.settings['login_url'], {
                    'next': self.request.uri,
                 }
            ))
