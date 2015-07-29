import ckan.plugins.toolkit as toolkit
import ckan.plugins as plugins
import ckan.lib.base as base
import ckan.logic as logic
import os
import json
from ckan.lib.plugins import DefaultGroupForm

from ckan.controllers.home import HomeController

import logging

import datetime
from sqlalchemy import Table
from sqlalchemy import Column
from sqlalchemy import types
from sqlalchemy import ForeignKey
from sqlalchemy.engine.reflection import Inspector

from ckan import model

from ckan.model.meta import metadata, mapper, Session, engine
from ckan.model.types import make_uuid
from ckan.model.domain_object import DomainObject
from ckanext.tess.model.tables import TessWorkflow

import ckan.lib.helpers as h

import ckan.authz as authz

abort = base.abort

get_action = logic.get_action
parse_params = logic.parse_params
redirect = base.redirect
NotFound = logic.NotFound

log = logging.getLogger(__name__)

tess_workflow_table = None

from ckan.common import OrderedDict, c, g, request, _


class WorkflowApi(plugins.SingletonPlugin):
    plugins.implements(plugins.interfaces.IActions)

    def get_actions(self):
        return {
            'add_material_to_package': add_material_to_package,
            'remove_material_from_package': remove_material_from_package
        }


class WorkflowPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.ITemplateHelpers, inherit=True)
    plugins.implements(plugins.interfaces.IMapper, inherit=True)
    plugins.implements(plugins.IConfigurer, inherit=True)
    plugins.implements(plugins.IAuthFunctions)

    def get_helpers(self):
        return {
            'read_workflow_file': read_workflow_file,
            'training_material_options': training_material_options,
            'get_workflows_for_user': get_workflows_for_user,
            'available_packages': available_packages,

        }

    def before_map(self, map):
        # <Placeholders>
        map.connect('workflow_activities', '/workflow/activities/{id}', controller='ckanext.tess.workflow:WorkflowController', action='index', ckan_icon='time')
        map.connect('workflow_materials', '/workflow/materials/{id}', controller='ckanext.tess.workflow:WorkflowController', action='display_workflow_materials', ckan_icon='book')
        # </placeholders>
        map.connect('workflow', '/workflow', controller='ckanext.tess.workflow:WorkflowController', action='index')
        map.connect('workflow_list', '/workflow', controller='ckanext.tess.workflow:WorkflowController', action='index')
        map.connect('workflow_new', '/workflow/new', controller='ckanext.tess.workflow:WorkflowController', action='new')

        map.connect('workflow_training_edit', '/workflow/edit_training', controller='ckanext.tess.workflow:WorkflowController', action='edit_training', ckan_icon="book")
        map.connect('workflow_training_read', '/workflow/read_training', controller='ckanext.tess.workflow:WorkflowController', action='read_training', ckan_icon="book")

        map.connect('workflow_update', '/workflow/edit/{id}', controller='ckanext.tess.workflow:WorkflowController', action='update')
        map.connect('workflow_delete', '/workflow/delete/{id}', controller='ckanext.tess.workflow:WorkflowController', action='delete')
        map.connect('workflow_read', '/workflow/{id}', controller='ckanext.tess.workflow:WorkflowController', action='read', ckan_icon="sitemap")

        map.connect('user_dashboard_workflows', '/dashboard/workflows', controller='ckanext.tess.workflow:WorkflowController', action='dashboard_workflows', ckan_icon='sitemap')
        return map

    def get_auth_functions(self):
        #unauthorized = lambda context, data_dict: {'success': False}
        authorized = lambda context, data_dict: {'success': True}
        return {
            'workflow_list': authorized,
            'workflow_show': authorized, # action to show/view workflow
            'workflow_new': workflow_actions_authz, # action to render a new workflow form
            'workflow_create': workflow_actions_authz, # create a new workflow in the database
            'workflow_update': workflow_actions_authz,
            'workflow_delete': workflow_actions_authz
        }


def add_material_to_package(context, data_dict):
    data_dict = {"id": data_dict.get('package_id'),
                 "object": data_dict.get('material_id'),
                 "object_type": 'package',
                 "capacity": 'public'}
    try:
        get_action('member_create')(context, data_dict)
    except NotFound:
        abort(404, _('Group not found'))


def remove_material_from_package(context, data_dict):
    data_dict = {"id": data_dict.get('package_id'),
                 "object": data_dict.get('material_id'),
                "object_type": 'package'}
    try:
        get_action('member_delete')(context, data_dict)
    except NotFound:
        return {'error': {'message': 'Could not complete this action as the package could not be found'}}

'''
Returns a graph structure of the workflow stages in the form of a dictionary e.g.
{   u'n0': {u'n1': {}, u'n2': {}, u'n3': {}, 'root': True, u'n4': {}},
    u'n4': {u'n5': {}, u'n6': {}, u'n7': {}},
    u'n7': {u'n8': {}, u'n9': {}}
}
The top level keys are all parents. In this example the first one 'n0' is root
The second top level one ('n4') is a child of n0. The third top level ('n7') is a child of
n7. All other nodes are leaf nodes.
'''
def node_structure(workflow_description):
    nodes = workflow_description.get('elements').get('nodes')
    node_graph = {}
    for node in nodes:
        node_dict = node.get('data')
        id = node_dict.get('id')
        parent = node_dict.get('parent')
        if not parent:  # Then it's a parent
            print 'node %s is a root node' % node_dict.get('id')
            node_graph[id] = {'root': True}
        else:  # Then it's a child
            print 'parent node of %s is %s' % (node_dict.get('id'), node_dict.get('parent'))
            # Add the child to the parent. Create the parent if it does not exist.
            # This will leave orphaned structures
            if not node_graph.get(parent):
                node_graph[parent] = {}
            node_graph[parent][id] = {}
    return node_graph

'''
Returns a flat list of node content e.g.
 {
  'n0': {'name': 'stage1', 'description': 'this is a description', 'materials': ['234234', '432432432']},
  'n1': {'name': 'stage2', 'description': 'this is a description', 'materials': ['234234', '432432432', '093402']}
 }
'''
def node_content(workflow_description):
    elements = workflow_description.get('elements')
    nodes = elements.get('nodes')
    node_content = {}
    if nodes:
        for node in nodes:
            node_data = node.get('data')
            node_content[node_data.get('id')] = {
                'name': node_data.get('name', 'Unnamed Node'),
                'description': node_data.get('description', None),
                'materials': node_data.get('materials', [])
            }
    return node_content


def training_material_options():
    res = toolkit.get_action('package_search')(data_dict={'rows': 5000})
    titles = []
    for package in res.get('results'):
        titles.append({'value': package['title'], 'id': package['id']})
    return titles

def get_workflows_for_user(user_id):

        workflows = model.Session.query(TessWorkflow).filter(TessWorkflow.creator_user_id == user_id)
        results = []
        for workflow in workflows:
            result = {}
            result['definition'] = workflow.definition
            result['name'] = workflow.name
            result['description'] = workflow.description
            result['id'] = workflow.id
            result['creator'] = model.User.get(workflow.creator_user_id).display_name
            result['created'] = h.time_ago_from_timestamp(workflow.created)
            result['modified'] = h.time_ago_from_timestamp(workflow.last_modified)
            results.append(result)
        return results

def available_packages(material_id):
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'for_view': True,
                   'auth_user_obj': c.userobj, 'use_cache': False}
        data_dict = {'id': material_id}
        material_dict = get_action('package_show')(context, data_dict)
        materials_packages = material_dict.get('groups', [])

        context['is_member'] = True
        users_packages = get_action('group_list_authz')(context, data_dict)

        # Remove all groups which type is set to 'node'
        for item in users_packages[:]:
            if item['type'] == 'node':
                users_packages.remove(item)

        material_packages_ids = set(package['id'] for package
                         in materials_packages)

        users_packages_ids = set(package['id'] for package
                          in users_packages)

        print 'materials packages = %s \n' % material_packages_ids
        print 'users packages = %s \n' % users_packages_ids

        associated_packages = [[package['id'], package['display_name']]
                           for package in users_packages if
                           package['id'] in material_packages_ids
                           and package['type'] == 'group']

        available_packages = [[package['id'], package['display_name']]
                           for package in users_packages if
                           package['type'] == 'group']

        return {'available': available_packages, 'associated': associated_packages}

def get_workflow(workflow_id):
    workflow = model.Session.query(TessWorkflow).get(workflow_id)
    result = {}
    if not workflow:
        abort(404, 'Workflow Not Found')
    result['definition'] = workflow.definition
    result['name'] = workflow.name
    result['description'] = workflow.description
    result['id'] = workflow.id
    result['creator'] = model.User.get(workflow.creator_user_id)
    result['created'] = workflow.created
    result['last_modified'] = workflow.last_modified
    return result


class WorkflowController(HomeController):

    def read_training(self):
        # Get all training materials for the node with node_id of workflow with workflow_id
        # Get all packages for each training material and all packages it can be assigned to
        try:
            parameters = logic.parse_params(request.params)
            workflow = get_workflow(parameters.get('workflow_id'))
            wf = json.loads(workflow.get('definition'))
            c.node = node_content(wf).get(parameters.get('node_id'))
            c.material_package = {}
            if c.userobj:
                for material in c.node.get('materials'):
                    c.material_package[material.get('id')] = available_packages(material.get('id'))

            return base.render('workflow/ajax/read_training.html', extra_vars={'open_modal_url': request.url})
        except Exception:
            return base.render('workflow/ajax/read_training.html')



    def edit_training(self):
        c.training_materials = training_material_options()
        return base.render('workflow/ajax/edit_training.html')

    def display_workflow_materials(self, id=None):
        c.workflow_dict = get_workflow(id)
        wf = json.loads(c.workflow_dict.get('definition'))
        node_materials = []
        c.node_structure = node_structure(wf)
        c.node_content = node_content(wf)
        return base.render('workflow/training_materials.html')

    def index(self):
        workflows = model.Session.query(TessWorkflow)
        results = []
        for workflow in workflows:
            result = {}
            result['definition'] = workflow.definition
            result['name'] = workflow.name
            result['description'] = workflow.description
            result['id'] = workflow.id
            result['creator'] = model.User.get(workflow.creator_user_id).display_name
            result['created'] = h.time_ago_from_timestamp(workflow.created)
            result['modified'] = h.time_ago_from_timestamp(workflow.last_modified)
            results.append(result)
        c.workflows = results
        return base.render('workflow/index.html')

    def new(self):
        parameters = logic.parse_params(request.params)
        if 'save' in parameters:
            wf_definition = parameters.get('dialog-div')
            wf_json = json.loads(wf_definition)
            print 'old def: ', json.dumps(wf_json)
            # if wf.get('elements') != {}:
            if wf_json.get('elements') == {}:
                wf_json[u'elements'] = {u'nodes':[], u'edges':[]} # empty wf
            new_model = TessWorkflow()
            new_model.name = parameters.get('title')
            new_model.description = parameters.get('description')
            new_model.definition = json.dumps(wf_json)
            print 'new def: ', new_model.definition
            user_obj = model.User.by_name(c.user.decode('utf8'))
            if user_obj:
                new_model.creator_user_id = user_obj.id
            new_model.save()
            id = new_model.id
            h.flash_notice('%s has been saved' % (parameters.get('title') or 'Workflow'))
            return h.redirect_to(controller='ckanext.tess.workflow:WorkflowController', action='read', id=id)
            # else:
            #     h.flash_warning('Whoops! It looks like you have not added any nodes to your workflow. Are you sure you want to save an empty workflow?')
            #     c.workflow_dict = {}
            #     c.workflow_dict['name'] = parameters.get('title')
            #     c.workflow_dict['description'] = parameters.get('description')
            #     return base.render('workflow/new.html')
        else:
            return base.render('workflow/new.html')

    def read(self, id=None):
        if id is None:
            abort(404, _('Workflow id can not be null'))

        #context = {'model': model, 'session': model.Session,
        #           'user': c.user or c.author,
        #           'schema': None,
        #           'for_view': True}
        #data_dict = {'id': id}

        c.workflow_dict = get_workflow(id)
        return base.render('workflow/read.html')

    def create(self):
        print "workflow create action"
        #workflow = TessWorkflow.new()
        #workflow_id = workflow.get('id')
        # ... set values, then something like:
        # workflow.commit()
        print request.params
        return base.render('workflow/new.html')

    def delete(self, id):
        workflow = model.Session.query(TessWorkflow).get(id)
        workflow.delete()
        workflow.commit()
        h.flash_notice('%s has been deleted' % (workflow.name or 'Workflow'))
        return h.redirect_to(controller='ckanext.tess.workflow:WorkflowController', action='index')

    def update(self, id):
        parameters = logic.parse_params(request.params)
        if 'save' in parameters:
            wf = json.loads(parameters.get('dialog-div'))
            if wf.get('elements') == {}:
                wf['elements'] = {"nodes":[], "edges":[]} # empty wf
            workflow = model.Session.query(TessWorkflow).get(id)
            workflow.name = parameters.get('title')
            workflow.description = parameters.get('description')
            if parameters.get('dialog-div'):
                workflow.definition = parameters.get('dialog-div')
            workflow.last_modified = datetime.datetime.utcnow()
            workflow.save()
            id = workflow.id
            h.flash_notice('%s has been updated' % (parameters.get('title') or 'Workflow'))
            return h.redirect_to(controller='ckanext.tess.workflow:WorkflowController', action='read', id=id)
            # else:
            #     h.flash_error('Whoops! It looks like your Training Workflow is empty. Please add stages to update.')
            #     c.workflow_dict = get_workflow(id)
            #     c.workflow_dict['name'] = parameters.get('title')
            #     c.workflow_dict['description'] = parameters.get('description')
            #     return base.render('workflow/edit.html')
        else:
            c.workflow_dict = get_workflow(id)

        return base.render('workflow/edit.html')


    def dashboard_workflows(self):
        context = {'for_view': True, 'user': c.user or c.author,
                   'auth_user_obj': c.userobj}
        data_dict = {'user_obj': c.userobj}

        c.is_sysadmin = authz.is_sysadmin(c.user)
        try:
            user_dict = get_action('user_show')(context, data_dict)
        except NotFound:
            abort(404, _('User not found'))
        except NotAuthorized:
            abort(401, _('Not authorized to see this page'))

        c.user_dict = user_dict
        c.is_myself = user_dict['name'] == c.user
        c.about_formatted = h.render_markdown(user_dict['about'])

        c.user_dict['workflows'] = get_workflows_for_user(user_dict['id'])

        return base.render('user/dashboard_workflows.html')


class TessDomainObject(DomainObject):
    # Convenience methods for searching objects, ripped off
    # from the original ckanext-harvest package.
    key_attr = 'id'

    @classmethod
    def get(cls, key, default=None, attr=None):
        '''Finds a single entity in the register.'''
        if attr == None:
            attr = cls.key_attr
        kwds = {attr: key}
        o = cls.filter(**kwds).first()
        if o:
            return o
        else:
            return default

    @classmethod
    def filter(cls, **kwds):
        query = Session.query(cls).autoflush(False)
        return query.filter_by(**kwds)


def workflow_actions_authz(context, data_dict=None):
    # All registered users can perform workflow operations: new, create, update, delete.
    # Any user (even if not registered) can do: list and read.

    username = context.get('user')
    user = _get_user(username)

    # # Get a list of the members of the 'curators' group.
    # members = toolkit.get_action('member_list')(
    #     data_dict={'id': 'curators', 'object_type': 'user'})
    #
    # # 'members' is a list of (user_id, object_type, capacity) tuples, we're
    # # only interested in the user_ids.
    # member_ids = [member_tuple[0] for member_tuple in members]
    #
    # # We have the logged-in user's user name, get their user id.
    # convert_user_name_or_id_to_id = toolkit.get_converter(
    #     'convert_user_name_or_id_to_id')
    # user_id = convert_user_name_or_id_to_id(user_name, context)
    #
    # # Finally, we can test whether the user is a member of the curators group.
    # if user_id in member_ids:
    #     return {'success': True}
    # else:
    #     return {'success': False,
    #             'msg': 'Only curators are allowed to create groups'}

    if user:
        # deleted users are always unauthorized
        if user.is_deleted():
            return {'success': False, 'msg': 'The user has been deleted and is not allowed to perform this action'}
            # sysadmins can do anything unless the auth_sysadmins_check
            # decorator was used in which case they are treated like all other
            # users.
        else:
            return {'success': True}
        endif
    else:
        return {'success': False, 'msg': 'Only registered users can perform this action'}
    endif

def _get_user(username):
    ''' Try to get the user from c, if possible, and fallback to using the DB '''
    if not username:
        return None
    # See if we can get the user without touching the DB
    try:
        if c.userobj and c.userobj.name == username:
            return c.userobj
    except TypeError:
        # c is not available
        pass
    # Get user from the DB
    return model.User.get(username)


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