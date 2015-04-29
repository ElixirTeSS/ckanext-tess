
import ckan.plugins.toolkit as toolkit
import ckan.plugins as plugins
import ckan.lib.base as base
import ckan.logic as logic
import os
import yaml as yaml
get_action = logic.get_action
parse_params = logic.parse_params
redirect = base.redirect
NotFound = logic.NotFound

from ckan.lib.plugins import DefaultGroupForm


def read_workflow_file(relative_file_path):
    '''
    :return: JSON/YAML representation of the workflow in cytoscape format
    '''
    here = os.path.dirname(__file__)
    file = os.path.join(here, relative_file_path)
    workflow = {}
    workflow_file = open(file, 'r')
    try:
        workflow = workflow_file.read()
    except Exception, e:
        print "Error reading workflow file " + file
        print e
    # print workflow
    return workflow

class WorkflowPlugin(plugins.SingletonPlugin, DefaultGroupForm):
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.ITemplateHelpers, inherit=True)
    plugins.implements(plugins.interfaces.IMapper, inherit=True)

    def get_helpers(self):
        return {
            'read_workflow_file' : read_workflow_file
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