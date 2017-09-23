from dockerspawner import DockerSpawner
from tornado import gen
import re
import os.path
import sys
import yaml


class ShellCommand:
    def __init__(self, commands=[]):
        self.commands = commands

    def add_commands(self, commands_list):
        self.commands.extend(commands_list)

    def extend(self, command):
        self.add_commands(command.commands)

    def get_single_command(self):
        return 'bash -c "{}"' .format(' && '.join(self.commands))

def make_git_command(repourl, commit_sha):
    return ShellCommand([
        'apt-get install -y git',
        'git clone {} /notebooks'.format(repourl),
        'cd /notebooks',
        'git reset --hard {}'.format(commit_sha)
    ])

def make_nginx_start_command(nginx_config):
    return ShellCommand([
        'apt-get install -y nginx',
        "python -c 'print(\\\"{}\\\")' >/etc/nginx/nginx.conf".format(nginx_config),
        'service nginx restart',
        'cat /etc/nginx/nginx.conf'
    ])

def make_default_start_command(env):
    return ShellCommand([
        'jupyterhub-singleuser --port=8888 --ip=0.0.0.0 --allow-root --user={} --cookie-name={} --base-url={} '.format(
            env['JPY_USER'],
            env['JPY_COOKIE_NAME'],
            env['JPY_BASE_URL']
        ) + '--hub-prefix={} --hub-api-url={} --notebook-dir=/notebooks'.format(
            env['JPY_HUB_PREFIX'],
            env['JPY_HUB_API_URL']
        )
    ])

def make_custom_start_command(command):
    return ShellCommand([command])


class ContainerHandler(DockerSpawner):
    def parse_config(self, directory):
        self.everware_config = {
            'everware_based': True
        }
        try:
            with open(os.path.join(directory, 'everware.yml')) as fin:
                try:
                    self.everware_config = yaml.load(fin)
                except yaml.YAMLError as exc:
                    self.log.warn('Fail reading everware.yml: {}'.format(exc))
        except IOError:
            self.log.info('No everware.yaml in repo')

    @gen.coroutine
    def prepare_container(self):
        if self.everware_config.get('everware_based', True):
            return
        container = yield self.get_container()
        was_cloned = yield self._check_for_git_compatibility(container)
        if not was_cloned:
            command = make_git_command(self.repo_url_with_token, self.commit_sha)
            setup = yield self.docker(
                'exec_create',
                container=container,
                cmd=command.get_single_command()
            )
            output = yield self.docker('exec_start', exec_id=setup['Id'])


    @gen.coroutine
    def start(self, image=None):
        self.parse_config(self._repo_dir)
        start_command = None
        extra_create_kwargs = {
            'ports': [self.container_port]
        }
        if not self.everware_config.get('everware_based', True):
            start_command = make_git_command(self.repo_url_with_token, self.commit_sha)
            if 'start_command' in self.everware_config:
                nginx_config = self._get_nginx_config(
                    8888,
                    self.custom_service_token(),
                    self.user.name
                )
                start_command.extend(make_nginx_start_command(nginx_config))
                start_command.extend(make_custom_start_command(self.everware_config['start_command']))
            else:
                start_command.extend(make_default_start_command(self.get_env()))
            extra_create_kwargs.update({
                'command': start_command.get_single_command()
            })

        extra_host_config = {
            'port_bindings': {
                self.container_port: (self.container_ip,)
            }
        }
        ip, port = yield DockerSpawner.start(self, image,
                            extra_create_kwargs=extra_create_kwargs,
                            extra_host_config=extra_host_config)
        return ip, port

    def _encode_conf(self, s):
        return ''.join('\\x' + hex(ord(x))[2:].zfill(2) for x in s)

    def _get_nginx_config(self, port, token, username):
        try:
            result = ''
            with open('etc/nginx_config.conf') as fin:
                for line in fin:
                    result += self._encode_conf(
                        line.replace('%TOKEN%', token)
                        .replace('%USERNAME%', username)
                        .replace('%PORT%', str(port))
                    )
            return result
        except OSError:
            self.log.warn('No nginx config')
            raise

    @gen.coroutine
    def _check_for_git_compatibility(self, container):
        setup = yield self.docker(
            'exec_create',
            container=container,
            cmd="bash -c \"ls / | grep -E '\\bnotebooks\\b'\""
        )
        output = yield self.docker('exec_start', exec_id=setup['Id'])
        return output != ""
