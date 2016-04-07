from tornado import web, gen

from docker.errors import NotFound
from jupyterhub.handlers.base import BaseHandler
from IPython.html.utils import url_path_join
from tornado.httputil import url_concat
from tornado.httpclient import HTTPRequest, AsyncHTTPClient
import json

import re

@gen.coroutine
def _fork_github_repo(url, token):
    http_client = AsyncHTTPClient()

    headers={"User-Agent": "JupyterHub",
             "Authorization": "token {}".format(token)
    }

    result = re.findall('^https://github.com/([^/]+)/([^/]+).*', url)
    if not result:
        raise ValueError('URL is not a github URL')

    owner, repo = result[0]

    api_url = "https://api.github.com/repos/%s/%s/forks" % (owner, repo)

    req = HTTPRequest(api_url,
                      method="POST",
                      headers=headers,
                      body='',
                      )

    resp = yield http_client.fetch(req)
    return json.loads(resp.body.decode('utf8', 'replace'))

@gen.coroutine
def _github_fork_exists(username, url, token):
    http_client = AsyncHTTPClient()

    headers={"User-Agent": "JupyterHub",
             "Authorization": "token {}".format(token)
    }

    result = re.findall('^https://github.com/([^/]+)/([^/]+).*', url)
    if not result:
        raise ValueError('URL (%s) is not a github URL' % url)

    owner, repo = result[0]
    api_url = "https://api.github.com/repos/%s/%s" % (username, repo)

    req = HTTPRequest(api_url,
                      method="GET",
                      headers=headers,
                      )

    try:
        resp = yield http_client.fetch(req)
        return True
    except:
        return False

@gen.coroutine
def _repository_changed(user):
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

@gen.coroutine
def _push_github_repo(user, url, commit_sha, branch_name, token):
    result = re.findall('^https://github.com/([^/]+)/([^/]+).*', url)
    if not result:
        raise ValueError('URL is not a github URL')

    owner, repo = result[0]
    fork_url = "https://{}@github.com/{}/{}".format(token, user.name, repo)

    out = yield user.spawner.docker(
            'exec_create',
            container=user.spawner.container_id,
            cmd="bash -c 'cd $JPY_WORKDIR && \
                 git config --global user.email \"everware@everware.xyz\" && \
                 git config --global user.name \"Everware\" && \
                 (git fetch --unshallow; true) && \
                 git add . && \
                 git commit -m \"Update through everware\" && \
                 (git remote add everware-fork {fork_url}; true) && \
                 git push -f everware-fork {branch_name}'".format(
                    fork_url=fork_url,
                    commit_sha=commit_sha,
                    branch_name=branch_name
                ),
            )
    response = yield user.spawner.docker(
            'exec_start',
            exec_id=out['Id'],
    )

class HomeHandler(BaseHandler):
    """Render the user's home page."""

    @web.authenticated
    @gen.coroutine
    def get(self):
        user = self.get_current_user()
        repourl = self.get_argument('repourl', '')
        do_fork = self.get_argument('do_fork', False)
        do_push = self.get_argument('do_push', False)
        if repourl:
            self.log.info('Got %s in home' % repourl)
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
        if user.running and hasattr(user, 'login_service'):
            branch_name = user.spawner.branch_name
            commit_sha = user.spawner.commit_sha
            if user.login_service == "github":
                if do_fork:
                    self.log.info('Will fork %s' % user.spawner.repo_url)
                    yield _fork_github_repo(
                            user.spawner.repo_url,
                            user.token,
                        )
                    self.redirect('/hub/home')
                    return
                if do_push:
                    self.log.info('Will push to fork')
                    yield _push_github_repo(
                            user,
                            user.spawner.repo_url,
                            commit_sha,
                            branch_name,
                            user.token,
                        )
                    self.redirect('/hub/home')
                    return
                repo_url = user.spawner.repo_url
                fork_exists = yield _github_fork_exists(
                                        user.name,
                                        user.spawner.repo_url,
                                        user.token,
                                    )
                repository_changed = yield _repository_changed(user)

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
            commit_sha=commit_sha
        )

        self.finish(html)

