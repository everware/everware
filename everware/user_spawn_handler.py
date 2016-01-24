from tornado import gen, web

from jupyterhub.handlers.pages import BaseHandler
from IPython.html.utils import url_path_join
from tornado.httputil import url_concat


class UserSpawnHandler(BaseHandler):
    """Requests to /user/name handled by the Hub
    should result in spawning the single-user server and
    being redirected to the original.
    """

    def _process_logs(self, logs):
        """prepare log for html"""

        return '\n'.join(cur.rstrip('\r\n') for cur in logs)

    @gen.coroutine
    def get(self, name):
        current_user = self.get_current_user()
        repo_url = self.get_argument('repo_url', '')
        if repo_url:
            current_user.last_repo_url = repo_url
        if current_user and current_user.name == name:
            # logged in, work with spawner
            if current_user.spawner:
                log_lines = self._process_logs(current_user.spawner.user_log)
                if not current_user.spawn_pending:
                    # user's server has started or
                    # even hasn't been created
                    is_running = yield current_user.spawner.is_running()
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
                log_lines = ''
            html = self.render_template(
                "spawn_pending.html",
                user=current_user,
                log_lines=log_lines
            )
            self.finish(html)
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
