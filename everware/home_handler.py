from tornado import web, gen
from tornado.escape import url_escape

from docker.errors import NotFound
from jupyterhub.handlers.base import BaseHandler
from IPython.html.utils import url_path_join
from tornado.httputil import url_concat

from .github_agent import *

@gen.coroutine
def is_repository_changed(user):
    try:
        setup = yield user.spawner.docker(
                'exec_create',
                container=user.spawner.container_id,
                cmd="bash -c 'cd $JPY_WORKDIR && \
                     (git fetch --unshallow > /dev/null 2>&1; true) && \
                     git diff --name-only'",
                )
        out = yield user.spawner.docker(
                'exec_start',
                exec_id=setup['Id'],
        )
    except NotFound:
        return False
    if out:
        return True
    else:
        return False


class HomeHandler(BaseHandler):
    """Render the user's home page."""

    @web.authenticated
    @gen.coroutine
    def get(self):
        user = self.get_current_user()
        repourl = self.get_argument('repourl', '')
        do_fork = self.get_argument('do_fork', False)
        do_push = self.get_argument('do_push', False)
        notify_message = self.get_argument('message', '')
        if repourl:
            self.redirect(url_concat(
                url_path_join(self.hub.server.base_url, 'spawn'), {
                    'repourl': repourl
                }
            ))
            return

        branch_name = commit_sha = None
        repo_url = ''
        fork_exists = False
        repository_changed = False
        if user.running:
            branch_name = user.spawner.branch_name
            commit_sha = user.spawner.commit_sha
            repo_url = user.spawner.repo_url
        if user.running and getattr(user, 'login_service', '') == 'github':
            if do_fork:
                self.log.info('Will fork %s' % user.spawner.repo_url)
                result = yield fork_repo(
                    user.spawner,
                    user.token
                )
                self.redirect(url_concat('/hub/home', dict(message='Successfully forked')))
                return
            if do_push:
                self.log.info('Will push to fork')
                result = yield push_repo(
                    user,
                    user.spawner,
                    user.token
                )
                result = str(result, 'ascii')
                self.log.info('Got after push: %s' % result)
                message = 'Successfully pushed'
                if 'Update through everware' not in result:
                    message = result
                self.redirect(url_concat('/hub/home', dict(message='Push result: %s' % message)))
                return
            fork_exists = yield does_fork_exist(
                user.name,
                user.spawner,
                user.token
            )
            repository_changed = yield is_repository_changed(user)

        if hasattr(user, 'login_service'):
            loginservice = user.login_service
        else:
            loginservice = 'none'
        html = self.render_template('home.html',
            user=user,
            repourl=repo_url,
            login_service=loginservice,
            fork_exists=fork_exists,
            repository_changed=repository_changed,
            branch_name=branch_name,
            commit_sha=commit_sha,
            notify_message=notify_message
        )

        self.finish(html)

