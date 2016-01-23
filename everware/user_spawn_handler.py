from tornado import gen, web

from jupyterhub.handlers.pages import BaseHandler
from IPython.html.utils import url_path_join


class UserSpawnHandler(BaseHandler):
    """Requests to /user/name handled by the Hub
    should result in spawning the single-user server and
    being redirected to the original.
    """
    @gen.coroutine
    def get(self, name):
        current_user = self.get_current_user()
        if current_user and current_user.name == name:
            # logged in, spawn the server
            if current_user.spawner:
                if current_user.spawn_pending:
                    # spawn has started, but not finished
                    logs = yield current_user.spawner.get_logs()
                    html = self.render_template(
                        "spawn_pending.html",
                        user=current_user,
                        log_lines=logs
                    )
                    self.finish(html)
                    return
                
                # spawn has supposedly finished, check on the status
                status = yield current_user.spawner.poll()
                if status is not None:
                    yield self.spawn_single_user(current_user)
            else:
                yield self.spawn_single_user(current_user)
            # set login cookie anew
            self.set_login_cookie(current_user)
            without_prefix = self.request.uri[len(self.hub.server.base_url):]
            target = url_path_join(self.base_url, without_prefix)
            self.redirect(target)
        else:
            # not logged in to the right user,
            # clear any cookies and reload (will redirect to login)
            self.clear_login_cookie()
            self.redirect(url_concat(
                self.settings['login_url'],
                {'next': self.request.uri,
            }))


