import ckan.lib.base as base
import ckan.controllers.group as group
from ckan.controllers.home import HomeController
import ckan.controllers.group as group

class SpecialRouteController(HomeController):
    def nodes(self):
        return base.render('nodes/index.html')       

    def events(self):
        return base.render('events.html')

    def workflows(self):
        return base.render('workflow/index.html')

class NodeController(group.GroupController):
    group_type = 'node'

    def _guess_group_type(self, expecting_name=False):
        return 'node'
