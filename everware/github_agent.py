from tornado import web, gen
from tornado.httpclient import HTTPRequest, AsyncHTTPClient
import json

from .git_processor import GitMixin

@gen.coroutine
def fork_repo(git_mixin, token):
    http_client = AsyncHTTPClient()
    headers={"User-Agent": "JupyterHub",
             "Authorization": "token {}".format(token)
    }

    if git_mixin.service != "github.com":
        raise ValueError("Not github in fork_repo")
    owner, repo = git_mixin.owner, git_mixin.repo
    api_url = "https://api.github.com/repos/%s/%s/forks" % (owner, repo)

    req = HTTPRequest(
        api_url,
        method="POST",
        headers=headers,
        body='',
    )
    resp = yield http_client.fetch(req)
    return json.loads(resp.body.decode('utf8', 'replace'))

@gen.coroutine
def does_fork_exist(username, git_mixin, token):
    http_client = AsyncHTTPClient()
    headers={"User-Agent": "JupyterHub",
             "Authorization": "token {}".format(token)
    }

    if git_mixin.service != "github.com":
        raise ValueError("Not a github in fork_exists")
    repo = git_mixin.repo
    api_url = "https://api.github.com/repos/%s/%s" % (username, repo)

    req = HTTPRequest(
        api_url,
        method="GET",
        headers=headers,
    )
    try:
        resp = yield http_client.fetch(req)
        return True
    except:
        return False


@gen.coroutine
def push_repo(user, git_mixin, token):
    repo, commit_sha, branch_name = git_mixin.repo, git_mixin.commit_sha, git_mixin.branch_name
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
    return response

