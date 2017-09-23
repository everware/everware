from tempfile import mkdtemp
from datetime import timedelta
from os.path import join as pjoin
from shutil import rmtree, copyfile
from pprint import pformat

from concurrent.futures import ThreadPoolExecutor

from docker.errors import APIError
from smtplib import SMTPException
from jupyterhub.utils import wait_for_http_server

from dockerspawner import DockerSpawner
from traitlets import (
    Integer,
    Unicode,
    Int,
    Bool,
    List,
    Dict
)
from tornado import gen
from tornado.httpclient import HTTPError

import ssl
import json
import os

from .image_handler import ImageHandler
from .git_processor import GitMixin
from .email_notificator import EmailNotificator
from .container_handler import ContainerHandler
from . import __version__


ssl._create_default_https_context = ssl._create_unverified_context


class CustomDockerSpawner(GitMixin, EmailNotificator, ContainerHandler):
    student_images = List(
        config=True,
        help="Mount student images for those",
    )

    student_volumes = Dict(
        config=True,
        help="Volumes to mount for student containers. In format of {host_path: container_path}. You can use {username} if needed."
    )

    student_host_homedir = Unicode(
        "/nfs/users/{username}",
        config=True,
        help="Path to the each student's home dir on host"
    )

    student_initial_files = List(
        config=True,
        help="Files to copy into student's folder",
    )

    def __init__(self, **kwargs):
        self._user_log = []
        self._is_failed = False
        self._is_up = False
        self._is_building = False
        self._image_handler = ImageHandler()
        self._cur_waiter = None
        self._is_empty = False
        ContainerHandler.__init__(self, **kwargs)
        EmailNotificator.__init__(self)

    # We override the executor here to increase the number of threads
    @property
    def executor(self):
        """single global executor"""
        cls = self.__class__
        if cls._executor is None:
            cls._executor = ThreadPoolExecutor(20)
        return cls._executor

    @staticmethod
    def get_global_client():
        return CustomDockerSpawner._client

    def _docker(self, method, *args, **kwargs):
        """wrapper for calling docker methods
        to be passed to ThreadPoolExecutor
        """
        # methods that return a generator object return instantly
        # before the work they were meant to do is complete
        generator_methods = ('build',)
        m = getattr(self.client, method)

        if method in generator_methods:
            def lister(mm):
                ret = []
                for l in mm:
                    for lj in l.decode().split('\r\n'):
                        if len(lj) > 0:
                            ret.append(lj)
                            try:
                                j = json.loads(lj)
                            except json.JSONDecodeError as e:
                                self.log.warn("Error decoding string to json: %s" % lj)
                            else:
                                if 'stream' in j and not j['stream'].startswith(' --->'):
                                    self._cur_waiter.add_to_log(j['stream'], 2)
                return ret
            return lister(m(*args, **kwargs))
        else:
            return m(*args, **kwargs)

    def clear_state(self):
        state = super(CustomDockerSpawner, self).clear_state()
        self.container_id = ''

    def get_state(self):
        state = DockerSpawner.get_state(self)
        state.update(GitMixin.get_state(self))
        state.update(dict(
            name=self.user.name,
        ))
        if hasattr(self.user, 'token'):
            state.update(dict(token=self.user.token))
        if hasattr(self.user, 'login_service'):
            state.update(dict(login_service=self.user.login_service))
        return state

    def load_state(self, state):
        DockerSpawner.load_state(self, state)
        GitMixin.load_state(self, state)
        for key in ('name', 'token', 'login_service'):
            if key in state:
                setattr(self.user, key, state[key])
        self.user.stop_pending = False
        self.user.spawn_pending = False

    def _options_form_default(self):
        return """
          <div class="mdl-textfield mdl-js-textfield mdl-textfield--floating-label" style="width: 50%">
            <input
              id="repository_input"
              type="text"
              autocapitalize="off"
              autocorrect="off"
              name="repository_url"
              tabindex="1"
              autofocus="autofocus"
              class="mdl-textfield__input"
            style="margin-bottom: 3px;" />
            <label class="mdl-textfield__label" for="repository_input">Git repository</label>
          </div>
          <label for="need_remove" class="mdl-checkbox mdl-js-checkbox mdl-js-ripple-effect" >
            <input type="checkbox"
                   name="need_remove"
                   class="mdl-checkbox__input"
                   id="need_remove"
                   checked />
            <span class="mdl-checkbox__label">Remove previous container if it exists</span>
          </label>
        """

    def options_from_form(self, formdata):
        options = {}
        options['repo_url'] = formdata.get('repository_url', [''])[0].strip()
        options.update(formdata)
        need_remove = formdata.get('need_remove', ['on'])[0].strip()
        options['need_remove'] = need_remove == 'on'
        if not options['repo_url']:
            raise Exception('You have to provide the URL to a git repository.')
        return options

    def custom_service_token(self):
        return self.user_options['service_token']

    @property
    def form_repo_url(self):
        """Repository URL as submitted by the user."""
        return self.user_options.get('repo_url', '')

    @property
    def container_name(self):
        return "{}-{}".format(self.container_prefix,
                              self.escaped_name)

    @property
    def need_remove(self):
        return self.user_options.get('need_remove', True)

    @property
    def is_empty(self):
        return self._is_empty

    @property
    def is_up(self):
        return self._is_up

    @gen.coroutine
    def get_container(self):
        try:
            container = yield self.docker(
                'inspect_container', self.container_name
            )
            self.container_id = container['Id']
        except APIError as e:
            if e.response.status_code == 404:
                # self.log.info("Container '%s' is gone", self.container_name)
                container = None
                # my container is gone, forget my id
                self.container_id = ''
            else:
                raise
        return container

    @gen.coroutine
    def get_image(self, image_name):
        images = yield self.docker('images')
        if ':' in image_name:
            tag_processor = lambda tag: tag
        else:
            tag_processor = lambda tag: tag.split(':')[0]
        for img in images:
            if not img['RepoTags']:
                continue
            tags = (tag_processor(tag) for tag in img['RepoTags'])
            if image_name in tags:
                return img

    @property
    def user_log(self):
        if self._is_building:
            build_log = getattr(self._cur_waiter, 'building_log', [])
            return self._user_log + build_log
        else:
            return self._user_log

    @property
    def is_failed(self):
        return self._is_failed

    @property
    def is_building(self):
        return self._is_building

    def _add_to_log(self, message, level=1):
        self._user_log.append({
            'text': message,
            'level': level
        })

    @gen.coroutine
    def wait_up(self):
        # copied from jupyterhub, because if user's server didn't appear, it
        # means that spawn was unsuccessful, need to set is_failed
        try:
            ip, port = yield self.get_ip_and_port()
            self.user.server.ip = ip
            self.user.server.port = port
            yield self.user.server.wait_up(http=True, timeout=self.http_timeout)
            self.user.server.ip = ip
            self.user.server.port = port
            self._is_up = True
        except TimeoutError:
            self._is_failed = True
            self._add_to_log('Server never showed up after {} seconds'.format(self.http_timeout))
            self.log.info("{user}'s server never showed up after {timeout} seconds".format(
                user=self.user.name,
                timeout=self.http_timeout
            ))
            yield self.notify_about_fail("Http timeout limit %.3f exceeded" % self.http_timeout)
            raise
        except Exception as e:
            self._is_failed = True
            message = str(e)
            self._add_to_log('Something went wrong during waiting for server. Error: %s' % message)
            yield self.notify_about_fail(message)
            raise e

    share_user_images = Bool(default_value=True, config=True, help="If True, users will be able restore only own images")

    def handle_student_case(self):
        if self.volumes is None:
            self.volumes = {}

        user_fmt = lambda s: s.format(username=self.user.name)
        host_dir = user_fmt(self.student_host_homedir)
        if not os.path.isdir(host_dir):
            os.mkdir(host_dir)
            os.chmod(host_dir, 0o777)

        for src_path in self.student_initial_files:
            filename = src_path.split("/")[-1]
            dst_path = pjoin(host_dir, filename)
            copyfile(src_path, dst_path)

        formatted_student_volumes = {
            user_fmt(k) : user_fmt(v) for k,v in self.student_volumes.items()
        }
        formatted_student_volumes[host_dir] = user_fmt("/home/{username}")
        self.volumes.update(formatted_student_volumes)

    @gen.coroutine
    def build_image(self):
        """download the repo and build a docker image if needed"""
        if self.form_repo_url.startswith('docker:'):
            image_name = self.form_repo_url.replace('docker:', '')

            if image_name.startswith('everware_image') and not self.user.admin and self.share_user_images:
                images_user = image_name.split('/')[1]
                if self.escaped_name != images_user:
                    raise Exception('Access denied. Image %s is not yours.' % image_name)

            image = yield self.get_image(image_name)
            if image is None:
                raise Exception('Image %s doesn\'t exist' % image_name)
            else:
                self._add_to_log('Image %s is found' % image_name)
                return image_name

        if self.form_repo_url in self.student_images:
            self.handle_student_case()

        tmp_dir = mkdtemp(suffix='-everware')
        try:
            self.parse_url(self.form_repo_url, tmp_dir)
            self._add_to_log('Cloning repository <a href="%s">%s</a>' % (
                self.repo_url,
                self.repo_url
            ))
            self.log.info('Cloning repo %s' % self.repo_url)
            dockerfile_exists = yield self.prepare_local_repo()
            if not dockerfile_exists:
                self._add_to_log('No dockerfile. Use the default one %s' % os.environ['DEFAULT_DOCKER_IMAGE'])

            # use git repo URL and HEAD commit sha to derive
            # the image name
            image_name = self.generate_image_name()

            self._add_to_log('Building image (%s)' % image_name)

            with self._image_handler.get_waiter(image_name) as self._cur_waiter:
                yield self._cur_waiter.block()
                image = yield self.get_image(image_name)
                if image is not None:
                    return image_name
                self.log.debug("Building image {}".format(image_name))
                build_log = yield self.docker(
                    'build',
                    path=tmp_dir,
                    tag=image_name,
                    pull=True,
                    rm=True,
                )
                self._user_log.extend(self._cur_waiter.building_log)
                full_output = "".join(str(line) for line in build_log)
                self.log.debug(full_output)
                image = yield self.get_image(image_name)
                if image is None:
                    raise Exception(full_output)
        except:
            raise

        return image_name

    def generate_image_name(self):
        return "everware/{}-{}".format(
            self.escaped_repo_url,
            self.commit_sha
        )

    @gen.coroutine
    def remove_old_container(self):
        try:
            yield self.docker(
                'remove_container',
                self.container_id,
                v=True,
                force=True
            )
        except APIError as e:
            self.log.info("Can't erase container %s due to %s" % (self.container_name, e))

    def _prepare_for_start(self):
        self._user_log = []
        self._is_up = False
        self._is_failed = False
        self._is_building = True
        self._is_empty = False

    @gen.coroutine
    def _start(self, image):
        """start the single-user server in a docker container"""
        try:
            f = self.build_image()
            image_name = yield gen.with_timeout(
                timedelta(seconds=self.start_timeout),
                f
            )
            self._is_building = False
            current_container = yield self.get_container()
            if self.need_remove and current_container:
                self.log.info('Removing old container %s' % self.container_name)
                self._add_to_log('Removing old container')
                yield self.remove_old_container()
            self.log.info("Starting container from image: %s" % image_name)
            self._add_to_log('Creating container')

            yield ContainerHandler.start(self,
                image=image_name
            )
        except gen.TimeoutError:
            self._is_failed = True
            if self._cur_waiter:
                self._user_log.extend(self._cur_waiter.building_log)
                self._cur_waiter.timeout_happened()
            self._add_to_log(
                'Building took too long (> %.3f secs)' % self.start_timeout,
                level=2
            )
            yield self.notify_about_fail("Timeout limit %.3f exceeded" % self.start_timeout)
            self._is_building = False
            raise
        except Exception as e:
            self._is_failed = True
            message = str(e)
            if message.startswith('Failed to get port'):
                message = "Container doesn't have jupyter-singleuser inside"
            self._add_to_log('Something went wrong during building. Error: %s' % message)
            yield self.notify_about_fail(message)
            self._is_building = False
            raise e
        finally:
            rmtree(self._repo_dir, ignore_errors=True)

        try:
            yield self.prepare_container()
        except Exception as e:
            self.log.warn('Fail to prepare the container: {}'.format(e))

        self._add_to_log('Adding to proxy')
        yield self.wait_up()
        return self.user.server.ip, self.user.server.port  # jupyterhub 0.7 prefers returning ip, port

    @gen.coroutine
    def start(self, image=None):
        self._prepare_for_start()
        ip_port = yield self._start(image)
        return ip_port

    @gen.coroutine
    def stop(self, now=False):
        """Stop the container
        Consider using pause/unpause when docker-py adds support
        """
        self._is_empty = True
        self.log.info(
            "Stopping container %s (id: %s)",
            self.container_name, self.container_id[:7])
        try:
            yield self.docker('stop', self.container_id)
        except APIError as e:
            message = str(e)
            self.log.warn("Can't stop the container: %s" % message)
            if 'container destroyed' not in message:
                raise
        else:
            if self.remove_containers:
                self.log.info(
                    "Removing container %s (id: %s)",
                    self.container_name, self.container_id[:7])
                # remove the container, as well as any associated volumes
                yield self.docker('remove_container', self.container_id, v=True)

        self.clear_state()

    @gen.coroutine
    def notify_about_fail(self, reason):
        email = os.environ.get('EMAIL_SUPPORT_ADDR')
        if not email:
            return
        self._user_log[-1]['text'] += """. We are notified about this error, please try again later.
            If it doesn't help, please contact everware support (%s).""" % email
        subject = "Everware: failed to spawn %s's server" % self.user.name
        message = "Failed to spawn %s's server from %s due to %s" % (
            self.user.name,
            self._repo_url, # use raw url (with commit sha and etc.)
            reason
        )
        from_email = os.environ['EMAIL_FROM_ADDR']
        try:
            yield self.executor.submit(self.send_email, from_email, email, subject, message)
        except SMTPException as exc:
            self.log.warn("Can't send a email due to %s" % str(exc))

    @gen.coroutine
    def poll(self):
        container = yield self.get_container()
        if not container:
            return ''

        container_state = container['State']
        self.log.debug(
            "Container %s status: %s",
            self.container_id[:7],
            pformat(container_state),
        )

        if container_state["Running"]:
            # check if something is listening inside container
            try:
                # self.log.info('poll {}'.format(self.user.server.url))
                yield wait_for_http_server(self.user.server.url, timeout=1)
            except TimeoutError:
                self.log.warn("Can't reach running container by http")
                return ''
            return None
        else:
            return (
                "ExitCode={ExitCode}, "
                "Error='{Error}', "
                "FinishedAt={FinishedAt}".format(**container_state)
            )

    @gen.coroutine
    def is_running(self):
        status = yield self.poll()
        return status is None

    def get_env(self):
        env = super(CustomDockerSpawner, self).get_env()
        env.update({
            'JPY_WORKDIR': '/notebooks'
        })
        if getattr(self, '_processed_repo_url', None): # if server was spawned via docker: link
            env.update({
                'JPY_GITHUBURL': self.repo_url_with_token,
                'JPY_REPOPOINTER': self.commit_sha,
                'NB_USER': self.user.name,
                'EVER_VERSION': __version__,
            })
            env.update(self.user_options)
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


    def generate_image_name(self):
        return "everware/{}-{}-{}".format(
            self.escaped_repo_url,
            self.user.name,
            self.commit_sha
        )


    @gen.coroutine
    def start(self, image=None, extra_create_kwargs=None):
        yield super(CustomSwarmSpawner, self).start(
            image=image
        )

        container = yield self.get_container()
        if container is not None:
            node_name = container['Node']['Name']
            self.user.server.ip = node_name
            self.db.commit()
            self.log.info("{} was started on {} ({}:{})".format(
                self.container_name, node_name, self.user.server.ip, self.user.server.port))
            return self.user.server.ip, self.user.server.port
