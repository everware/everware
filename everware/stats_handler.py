from jupyterhub.handlers.pages import BaseHandler
from docker import Client
from tornado import gen


class StatsHandler(BaseHandler):
    """Handler for the stats page ['/hub/stats'].

    Fills the page with some statistics on everware.
    """
    container_statuses = {
        'running': 'running',
        'restarting': 'restarting',
        'paused': 'paused',
        'exited': 'exited'
    }

    def initialize(self, stats):
        """Initialize the handler.

        Parameters
        ----------
        stats : dict
            A dict containing all the stats on the everware instance.
        """
        self.stats = stats

    @gen.coroutine
    def get(self, *args, **kwargs):
        running_container_count = yield self.get_running_container_count()
        html = self.render_template(
            'stats.html',
            running_container_count=running_container_count,
            total_launch_count=self.stats['total_launch_count']
        )
        self.finish(html)

    @gen.coroutine
    def get_running_container_count(self):
        """Get the number of currently running containers."""
        client = self.spawner_class.get_global_client()
        if client is None:
            # None means that there were no launches
            return 0
        return len(client.containers(filters={'status': self.container_statuses['running']}))
