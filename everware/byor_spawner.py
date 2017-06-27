from os.path import join as pjoin

import docker
from docker.errors import DockerException
from traitlets import Int
from tornado import gen

from .spawner import CustomDockerSpawner


class ByorDockerSpawner(CustomDockerSpawner):
    def __init__(self, **kwargs):
        CustomDockerSpawner.__init__(self, **kwargs)
        self._byor_client = None
        if self.options_form == self._options_form_default():
            with open(pjoin(self.config['JupyterHub']['template_paths'][0],
                            '_byor_options_form.html')) as form:
                ByorDockerSpawner.options_form = form.read()

    @property
    def client(self):
        if self._byor_client is not None:
            return self._byor_client
        return super(ByorDockerSpawner, self).client

    @property
    def byor_is_used(self):
        return self.user_options.get('byor_is_needed', False)

    def _reset_byor(self):
        self.container_ip = str(self.__class__.container_ip)
        self._byor_client = None

    byor_timeout = Int(20, min=1, config=True,
                       help='Timeout for connection to BYOR Docker daemon')

    def options_from_form(self, formdata):
        options = {}
        options['byor_is_needed'] = formdata.pop('byor_is_needed', [''])[0].strip() == 'on'
        for field in ('byor_docker_ip', 'byor_docker_port'):
            options[field] = formdata.pop(field, [''])[0].strip()
        options.update(
            super(ByorDockerSpawner, self).options_from_form(formdata)
        )
        return options

    @gen.coroutine
    def _configure_byor(self):
        """Configure BYOR settings or reset them if BYOR is not needed."""
        if not self.byor_is_used:
            self._reset_byor()
            return
        byor_ip = self.user_options['byor_docker_ip']
        byor_port = self.user_options['byor_docker_port']
        try:
            # version='auto' causes a connection to the daemon.
            # That's why the method must be a coroutine.
            self._byor_client = docker.Client('{}:{}'.format(byor_ip, byor_port),
                                              version='auto',
                                              timeout=self.byor_timeout)
        except DockerException as e:
            self._is_failed = True
            message = str(e)
            if 'ConnectTimeoutError' in message:
                log_message = 'Connection to the Docker daemon took too long (> {} secs)'.format(
                    self.byor_timeout
                )
                notification_message = 'BYOR timeout limit {} exceeded'.format(self.byor_timeout)
            else:
                log_message = "Failed to establish connection with the Docker daemon"
                notification_message = log_message
            self._add_to_log(log_message, level=2)
            yield self.notify_about_fail(notification_message)
            self._is_building = False
            raise

        self.container_ip = byor_ip

    @gen.coroutine
    def _prepare_for_start(self):
        super(ByorDockerSpawner, self)._prepare_for_start()
        yield self._configure_byor()

    @gen.coroutine
    def start(self, image=None):
        yield self._prepare_for_start()
        ip_port = yield self._start(image)
        return ip_port
