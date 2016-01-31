import re
import pwd
from tempfile import mkdtemp
from datetime import timedelta

from concurrent.futures import ThreadPoolExecutor

from docker.errors import APIError

from dockerspawner import DockerSpawner
from textwrap import dedent
from traitlets import (
    Integer,
    Unicode,
)
from tornado import gen
from tornado.ioloop import IOLoop

from escapism import escape

import git


class CustomDockerSpawner(DockerSpawner):
    poll_interval = Integer(
        30,
        config=True,
        help="""Interval (in seconds) on which to poll the spawner."""
    )

    def __init__(self, **kwargs):
        super(CustomDockerSpawner, self).__init__(**kwargs)
        self._user_log = []

    def _docker(self, method, *args, **kwargs):
        """
        wrapper for calling docker methods

        to be passed to ThreadPoolExecutor
        """
        # methods that return a generator object return instantly
        # before the work they were meant to do is complete
        generator_methods = ('build',)
        m = getattr(self.client, method)

        if method in generator_methods:
            self.log.info("run docker with block %s: %s, %s" %
                          (method, args, kwargs))

            def lister(mm):
                ret = []
                for l in mm:
                    ret.append(str(l))
                    # include only high-level docker's log
                    if 'stream' in l and not l['stream'].startswith(' --->'):
                        self._add_to_log(l['stream'], 2)
                return ret

            return lister(m(*args, **kwargs))
        else:
            return m(*args, **kwargs)

    _git_executor = None

    @property
    def git_executor(self):
        """single global git executor"""

        cls = self.__class__
        if cls._git_executor is None:
            cls._git_executor = ThreadPoolExecutor(1)
        return cls._git_executor

    _git_client = None

    @property
    def git_client(self):
        """single global git client instance"""

        cls = self.__class__
        if cls._git_client is None:
            cls._git_client = git.Git()
        return cls._git_client

    def _git(self, method, *args, **kwargs):
        """
        wrapper for calling git methods

        to be passed to ThreadPoolExecutor
        """

        m = getattr(self.git_client, method)
        return m(*args, **kwargs)

    def git(self, method, *args, **kwargs):
        """
        Call a git method in a background thread

        returns a Future
        """

        return self.git_executor.submit(self._git, method, *args, **kwargs)

    def clear_state(self):
        state = super(CustomDockerSpawner, self).clear_state()
        self.container_id = ''

    @property
    def repo_url(self):
        last_repo_url = getattr(self.user, 'last_repo_url', None)
        assert last_repo_url is not None, "Empty last_repo_url"
        return last_repo_url

    _escaped_repo_url = None

    @property
    def escaped_repo_url(self):
        if self._escaped_repo_url is None:
            self._escaped_repo_url = re.sub("[-:/._]+", "_", self.repo_url)
        return self._escaped_repo_url

    @property
    def container_name(self):
        return "{}-{}-{}-{}".format(
            self.container_prefix,
            self.escaped_name,
            self.escaped_repo_url,
            self.repo_sha
        )

#    @gen.coroutine
#    def get_container(self):
#        #if not self.container_id:
#        #    return None
#
#        self.log.debug("Getting container: %s", self.container_id)
#        try:
#            container = yield self.docker(
#                'inspect_container', self.container_id
#            )
#            self.container_id = container['Id']
#        except APIError as e:
#            if e.response.status_code == 404:
#                self.log.info("Container '%s' is gone", self.container_id)
#                container = None
#                # my container is gone, forget my id
#                self.container_id = ''
#            else:
#                raise
#        return container

    @gen.coroutine
    def get_image(self, image_name):
        images = yield self.docker('images')
        for img in images:
            tags = (tag.split(':')[0] for tag in img['RepoTags'])
            if image_name in tags:
                return img

    @property
    def user_log(self):
        return self._user_log

    def _add_to_log(self, message, level=1):
        self._user_log.append({
            'text': message,
            'level': level
        })

    @gen.coroutine
    def build_image(self):
        """download the repo and build a docker image if needed"""
        building_start = IOLoop.current().time()
        tmp_dir = mkdtemp(suffix='-everware')
        self._add_to_log('Cloning repository %s' % self.repo_url)
        yield self.git('clone', self.repo_url, tmp_dir)
        # is this blocking?
        # use the username, git repo URL and HEAD commit sha to derive
        # the image name
        repo = git.Repo(tmp_dir)
        self.repo_sha = repo.rev_parse("HEAD")

        image_name = "everware/{}-{}-{}".format(
            self.user.name,
            self.escaped_repo_url,
            self.repo_sha
        )

        self._add_to_log('Building image')

        image = yield self.get_image(image_name)
        if image is None:
            self.log.debug("Building image {}".format(image_name))
            build_log = yield self.docker(
                'build',
                path=tmp_dir,
                tag=image_name,
                rm=True,
                decode=True
            )
            self.log.debug("".join(str(line) for line in build_log))

        # If the build took too long, do not start the container
        building_end = IOLoop.current().time()
        if building_end - building_start > self.start_timeout:
            self.log.warn("Build timed out (image: %s)" % image_name)
            return
        return image_name

    @gen.coroutine
    def is_running(self):
        status = yield self.poll()
        return status is None

    @gen.coroutine
    def start(self, image=None):
        """start the single-user server in a docker container"""
        self._user_log = []
        image_name = yield self.build_image()
        self.log.info("Staring container from image: %s" % image_name)
        self._add_to_log('Creating container')
        yield super(CustomDockerSpawner, self).start(
            image=image_name
        )

    def _env_default(self):
        env = super(CustomDockerSpawner, self)._env_default()

        env.update({'JPY_GITHUBURL': self.repo_url})

        return env


class CustomSwarmSpawner(CustomDockerSpawner):
    container_ip = '0.0.0.0'
    #start_timeout = 42 #180

    def __init__(self, **kwargs):
        super(CustomSwarmSpawner, self).__init__(**kwargs)

    @gen.coroutine
    def lookup_node_name(self):
        """Find the name of the swarm node that the container is running on."""
        containers = yield self.docker('containers', all=True)
        for container in containers:
            if container['Id'] == self.container_id:
                name, = container['Names']
                node, container_name = name.lstrip("/").split("/")
                raise gen.Return(node)

    @gen.coroutine
    def start(self, image=None, extra_create_kwargs=None):
        yield super(CustomSwarmSpawner, self).start(
            image=image
        )

        container = yield self.get_container()
        if container is not None:
            node_name = container['Node']['Name']
            self.user.server.ip = node_name
            self.log.info("{} was started on {} ({}:{})".format(
                self.container_name, node_name, self.user.server.ip, self.user.server.port))
