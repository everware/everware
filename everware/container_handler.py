from dockerspawner import DockerSpawner
from tornado import gen
import sys

class ContainerHandler(DockerSpawner):
    @gen.coroutine
    def prepare_container(self, everware_based, need_service):
        self.debug_log = open('debug_log', 'w')
        container = yield self.get_container()
        if not everware_based or need_service:
            yield self._init_container(container, everware_based)
        if need_service:
            nginx_started = yield self._start_nginx(
                container,
                self.custom_service_token(),
                self.user.name
            )
            git_webui_started = False
            if nginx_started:
                self.log.info('nginx has started in %s' % self.container_id)
                git_webui_started = yield self._start_service(container)
                if git_webui_started:
                    self.log.info('git webui has started in %s' % self.container_id)
                    self._add_to_log('Git Web UI has started')
            if not git_webui_started:
                self._add_to_log('Failed to start git web ui')

        if everware_based:
            return

        yield self._run_all(container)

    def _encode_conf(self, s):
        return ''.join('\\x' + hex(ord(x))[2:].zfill(2) for x in s)

    @gen.coroutine
    def _start_nginx(self, container, token, username):
        try:
            result = ''
            with open('etc/nginx_config.conf') as fin:
                for line in fin:
                    result += self._encode_conf(
                        line.replace('%TOKEN%', token).replace('%USERNAME%', username)
                    )
            setup = yield self.docker(
                'exec_create',
                container=container,
                cmd="bash -c \"apt-get install nginx -y && " +\
                    "python -c 'print(\\\"%s\\\")' >/etc/nginx/nginx.conf && " % result +\
                    "service nginx restart && cat /etc/nginx/nginx.conf\""
            )
            output = yield self.docker('exec_start', exec_id=setup['Id'])
            print(output, file=self.debug_log)
        except OSError:
            self.log.info('No nginx config')
            return False
        return True

    @gen.coroutine
    def _start_service(self, container):
        setup = yield self.docker(
            'exec_create',
            container=container,
            cmd="bash -c '"+\
                "curl https://raw.githubusercontent.com/alberthier/git-webui/master/install/installer.sh >installer.sh" +\
                " && bash installer.sh && cd {} && git webui --port=8081 --host=0.0.0.0 --no-browser >/dev/null 2>/dev/null &'".format(
                    '/notebooks'
                )
        )
        output = yield self.docker('exec_start', exec_id=setup['Id'])
        print(output, file=sys.stderr)
        return True

    @gen.coroutine
    def _init_container(self, container, everware_based):
        cmd = "bash -c 'apt-get update && apt-get install git wget curl -y"
        if everware_based:
            cmd += "'"
        else:
            notebook_dir = '/notebooks'
            cmd += " && git clone {} {} && cd {} && git reset --hard {}'".format(
                self.repo_url_with_token,
                notebook_dir,
                notebook_dir,
                self.commit_sha
            )

        setup = yield self.docker(
            'exec_create',
            container=container,
            cmd=cmd
        )
        output = yield self.docker('exec_start', exec_id=setup['Id'])
        print(output, file=self.debug_log)

    @gen.coroutine
    def _run_all(self, container):
        setup = yield self.docker(
            'exec_create',
            container=container,
            cmd="bash -c 'apt-get install jupyter -y && "+\
                "curl https://raw.githubusercontent.com/jupyterhub/jupyterhub/master/jupyterhub/singleuser.py >singleuser.py" +\
                " && chmod +x singleuser.py && ./singleuser.py --port=8888 --ip=0.0.0.0 --no-browser &'"
        )
        output = yield self.docker('exec_start', exec_id=setup['Id'])
        print(output, file=self.debug_log)
