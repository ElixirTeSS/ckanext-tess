import ckan.lib.base as base
import ckan.controllers.group as group
from ckan.controllers.home import HomeController


class SpecialRouteController(HomeController):
    def node_old(self):
        return base.render('node_old/index.html')

    def events(self):
        return base.render('events.html')

    def workflows(self):
        return base.render('workflow/index.html')

class NodeController(group.GroupController):
    group_type = 'node'

    def _guess_group_type(self, expecting_name=False):
        return 'node'
