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

abort = base.abort

get_action = logic.get_action
parse_params = logic.parse_params
redirect = base.redirect
NotFound = logic.NotFound

log = logging.getLogger(__name__)

tess_workflow_table = None

from ckan.common import OrderedDict, c, g, request, _

class WorkflowPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.ITemplateHelpers, inherit=True)
    plugins.implements(plugins.interfaces.IMapper, inherit=True)
    plugins.implements(plugins.IConfigurer, inherit=True)
    plugins.implements(plugins.IAuthFunctions)

    def get_helpers(self):
        return {
            'read_workflow_file' : read_workflow_file,
            'training_material_options' : training_material_options
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


def training_material_options():
    res = toolkit.get_action('package_search')(data_dict={'rows': 5000})
    titles = []
    for package in res.get('results'):
        titles.append({'value': package['title'], 'id': package['id']})
    return titles


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
        return base.render('workflow/ajax/read_training.html')

    def edit_training(self):
        print
        c.training_materials = training_material_options()
        c.stage_name
        return base.render('workflow/ajax/edit_training.html')

    def display_workflow_materials(self, id=None):
        c.workflow_dict = get_workflow(id)
        wf = json.loads(c.workflow_dict.get('definition'))
        node_materials = []

        elements = wf.get('elements')
        nodes = elements.get('nodes')
        if nodes:
            for node in nodes:
                node_data = node.get('data')
                node_materials.append({'name': node_data.get('name', 'Unnamed Node'),
                                        'description': node_data.get('description', None),
                                        'materials': node_data.get('materials', [])})
        c.node_materials = node_materials
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