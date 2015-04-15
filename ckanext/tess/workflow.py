
import ckan.plugins.toolkit as toolkit
import ckan.plugins as plugins
import ckan.lib.base as base
import ckan.logic as logic
get_action = logic.get_action
parse_params = logic.parse_params
redirect = base.redirect
NotFound = logic.NotFound

from ckan.lib.plugins import DefaultGroupForm


class WorkflowPlugin(plugins.SingletonPlugin, DefaultGroupForm):
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.ITemplateHelpers, inherit=True)
    plugins.implements(plugins.interfaces.IMapper, inherit=True)

    def get_helpers(self):
        return {
        }

    def before_map(self, map):
        map.connect('workflow', '/workflow', controller='ckanext.tess.workflow:WorkflowController', action='workflows')
        map.connect('workflow-new', '/workflow/new', controller='ckanext.tess.workflow:WorkflowController', action='new')
        return map


from ckan.controllers.home import HomeController


class WorkflowController(HomeController):

    def workflows(self):
        return base.render('workflow/index.html')

    def new(self):
        return base.render('workflow/new.html')