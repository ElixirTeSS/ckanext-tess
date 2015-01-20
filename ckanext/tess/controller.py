import ckan.lib.base as base

from ckan.controllers.home import HomeController

class SpecialRouteController(HomeController):
    def nodes(self):
        return base.render('nodes/index.html')       

    def events(self):
        return base.render('events.html')

    def workflows(self):
        return base.render('workflow/index.html')
