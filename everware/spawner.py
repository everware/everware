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

from escapism import escape

import git


class CustomDockerSpawner(DockerSpawner):
    def __init__(self, **kwargs):
        super(CustomDockerSpawner, self).__init__(**kwargs)

    def _docker(self, method, *args, **kwargs):
        """wrapper for calling docker methods

        to be passed to ThreadPoolExecutor
        """
        # methods that return a generator object return instantly
        # before the work they were meant to do is complete
        generator_methods = ('build',)
        m = getattr(self.client, method)

        if method in generator_methods:
            return list(m(*args, **kwargs))
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
        """wrapper for calling git methods
        
        to be passed to ThreadPoolExecutor
        """
        m = getattr(self.git_client, method)
        return m(*args, **kwargs)

    def git(self, method, *args, **kwargs):
        """Call a git method in a background thread
        
        returns a Future
        """
        return self.git_executor.submit(self._git, method, *args, **kwargs)

    @property
    def repo_url(self):
        return self.user.last_repo_url

    _escaped_repo_url = None
    @property
    def escaped_repo_url(self):
        if self._escaped_repo_url is None:
            trans = str.maketrans(':/-.', "____")
            self._escaped_repo_url = self.repo_url.translate(trans)
        return self._escaped_repo_url

    @property
    def container_name(self):
        return "{}-{}".format(self.container_prefix,
                              self.escaped_name)

    @gen.coroutine
    def get_container(self):
        if not self.container_id:
            return None

        self.log.debug("Getting container: %s", self.container_id)
        try:
            container = yield self.docker(
                'inspect_container', self.container_id
            )
            self.container_id = container['Id']
        except APIError as e:
            if e.response.status_code == 404:
                self.log.info("Container '%s' is gone", self.container_id)
                container = None
                # my container is gone, forget my id
                self.container_id = ''
            else:
                raise
        return container

    @gen.coroutine
    def start(self, image=None):
        """start the single-user server in a docker container"""
        tmp_dir = mkdtemp(suffix='-everware')
        yield self.git('clone', self.repo_url, tmp_dir)
        # is this blocking?
        # use the username, git repo URL and HEAD commit sha to derive
        # the image name
        repo = git.Repo(tmp_dir)
        self.repo_sha = repo.rev_parse("HEAD")

        image_name = "everware/{}-{}-{}".format(self.user.name,
                                                self.escaped_repo_url,
                                                self.repo_sha)

        self.log.debug("Building image {}".format(image_name))
        build_log = yield self.docker('build',
                                      path=tmp_dir,
                                      tag=image_name,
                                      rm=True)
        self.log.debug("".join(str(line) for line in build_log))

        images = yield self.docker('images', image_name)
        self.log.debug(images)

        yield super(CustomDockerSpawner, self).start(
            image=image_name
        )

    def _env_default(self):
        env = super(CustomDockerSpawner, self)._env_default()

        env.update({'JPY_GITHUBURL': self.repo_url})

        return env


class CustomSwarmSpawner(CustomDockerSpawner):
    container_ip = '0.0.0.0'
    start_timeout = 180

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
        # look up mapping of node names to ip addresses
        info = yield self.docker('info')
        name_host = [(e[0], e[1].split(':')[0]) for e in info['DriverStatus'][4:] if len(e) == 2 and e[1].endswith('2375')]
        self.node_info = dict(name_host)
        self.log.debug("Swarm nodes are: {}".format(self.node_info))

        # start the container
        if extra_create_kwargs is None:
            extra_create_kwargs = {}
        if 'mem_limit' not in extra_create_kwargs:
            extra_create_kwargs['mem_limit'] = '1g'
        self.log.debug("Spawning container: {}, args: {}".format(image, extra_create_kwargs))

        yield super(CustomSwarmSpawner, self).start(
            image=image
        )
        
        # figure out what the node is and then get its ip
        name = yield self.lookup_node_name()
        self.user.server.ip = self.node_info[name]
        self.log.info("{} was started on {} ({}:{})".format(
            self.container_name, name, self.user.server.ip, self.user.server.port))
