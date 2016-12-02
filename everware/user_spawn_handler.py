from tornado import web, gen
import jupyterhub.handlers.pages as default_handlers
import sys
from . import __version__
from .metrica import MetricaIdsMixin

class SpawnHandler(default_handlers.SpawnHandler):

    @gen.coroutine
    def count_running_users(self):
        running_users = 0
        for user_id, user in self.users.items():
            if user.running:
                running_users += 1
        return running_users

    def _render_form(self, message=''):
        user = self.get_current_user()
        metrica = MetricaIdsMixin()
        g_id = metrica.g_analitics_id
        ya_id = metrica.ya_metrica_id
        return self.render_template('spawn.html',
            user=user,
            spawner_options_form=user.spawner.options_form,
            error_message=message,
            version=__version__,
            g_analitics_id=g_id,
            ya_metrica_id=ya_id
        )

    @gen.coroutine
    def _spawn(self, user, form_options):
        running_users = yield self.count_running_users()
        self.redirect('/user/%s' % user.name)
        try:
            options = user.spawner.options_from_form(form_options)
            options.update({
                'running_users': running_users
            })
            yield self.spawn_single_user(user, options=options)
            # if user set another access token (for example he logged with github
            # and clones from bitbucket)
            # Or clones from a private repo
            if user.spawner.token:
                user.token = user.spawner.token
        except Exception as e:
            self.log.error("Failed to spawn single-user server with form", exc_info=True)

    @web.authenticated
    def get(self):
        user = self.get_current_user()
        if user.running:
            name = user.name
            self.log.debug("User is running: %s", name)
            self.redirect('/user/%s' % name)
            return
        repourl = self.get_argument('repourl', '')
        all_arguments = {param: self.get_argument(param) for param in self.request.arguments}

        if repourl:
            options = {
                'repository_url': [repourl, ],
            }
            options.update(all_arguments)
            self._spawn(user, options)
        elif user.spawner.options_form:
            self.finish(self._render_form())

    @web.authenticated
    @gen.coroutine
    def post(self):
        """POST spawns with user-specified options"""
        user = self.get_current_user()
        if user.running:
            url = user.server.base_url
            self.log.warning("User is already running: %s", url)
            self.redirect(url)
            return
        form_options = {}
        for key, byte_list in self.request.body_arguments.items():
            form_options[key] = [ bs.decode('utf8') for bs in byte_list ]
        for key, byte_list in self.request.files.items():
            form_options["%s_file"%key] = byte_list
        self._spawn(user, form_options)
