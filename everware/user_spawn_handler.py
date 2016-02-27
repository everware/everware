from tornado import web, gen
import jupyterhub.handlers.pages as default_handlers

class SpawnHandler(default_handlers.SpawnHandler):

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
        # url = user.server.base_url
        self.redirect('/user/%s' % user.name)
        try:
            options = user.spawner.options_from_form(form_options)
            yield self.spawn_single_user(user, options=options)
        except Exception as e:
            self.log.error("Failed to spawn single-user server with form", exc_info=True)
