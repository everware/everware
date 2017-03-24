from dockerspawner import DockerSpawner
from tornado import gen
import re

class ContainerHandler(DockerSpawner):
    @gen.coroutine
    def prepare_container(self, need_service):
        container = yield self.get_container()
        everware_based = yield self._is_everware_compatible(container)
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
            else:
                self.log.info('failed to start nginx in %s' % self.container_id)
            if not git_webui_started:
                self._add_to_log('Failed to start git web ui')
                self.user_options['custom_service'] = False

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
            # print(output, file=self.debug_log)
            # print(str(output), file=sys.stderr)
            return re.search(
                r'Restarting nginx.+?\.\.\.done\.',
                str(output),
                flags=re.DOTALL
            )
        except OSError:
            self.log.info('No nginx config')
            return False

    @gen.coroutine
    def _start_service(self, container):
        setup = yield self.docker(
            'exec_create',
            container=container,
            cmd="bash -c '"+\
                "curl https://raw.githubusercontent.com/everware/git-webui/master/install/installer.sh >installer.sh" +\
                " && bash installer.sh && cd /notebooks; "+\
                "git webui --port=8081 --host=0.0.0.0 --no-browser >/dev/null 2>&1 &'"
        )
        output = yield self.docker('exec_start', exec_id=setup['Id'])
        return True

    @gen.coroutine
    def _init_container(self, container, everware_based):
        cmd = "bash -c 'apt-get update && apt-get install git curl net-tools -y"
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

    #@gen.coroutine
    #def _run_jupyter(self, container):
    #    setup = yield self.docker(
    #        'exec_create',
    #        container=container,
    #        cmd="bash -c 'apt-get install jupyter -y && "+\
    #            "curl https://raw.githubusercontent.com/jupyterhub/jupyterhub/master/jupyterhub/singleuser.py >singleuser.py" +\
    #            " && chmod +x singleuser.py && ./singleuser.py --port=8888 --ip=0.0.0.0 --no-browser &'"
    #    )
    #    output = yield self.docker('exec_start', exec_id=setup['Id'])
    #    print(output, file=self.debug_log)

    @gen.coroutine
    def _is_everware_compatible(self, container):
        setup = yield self.docker(
            'exec_create',
            container=container,
            cmd="bash -c \"ls / | grep -E '\\bnotebooks\\b'\""
        )
        output = yield self.docker('exec_start', exec_id=setup['Id'])
        return output != ""

    #@gen.coroutine
    #def _is_jupyter_inside(self, container):
    #    setup = yield self.docker(
    #        'exec_create',
    #        container=container,
    #        cmd="bash -c 'netstat -peant | grep \":8888 \"'"
    #    )
    #    output = yield self.docker('exec_start', exec_id=setup['Id'])
    #    print('jupyter check:', output, file=sys.stderr)
    #    return output != ""
