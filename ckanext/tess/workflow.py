import ckan.plugins.toolkit as toolkit
import ckan.plugins as plugins
import ckan.lib.base as base
import ckan.logic as logic
import os

from ckan.lib.plugins import DefaultGroupForm

from ckan.controllers.home import HomeController

import logging

from sqlalchemy import Table
from sqlalchemy import Column
from sqlalchemy import types
from sqlalchemy import ForeignKey
from sqlalchemy.engine.reflection import Inspector

from ckan import model

from ckan.model.meta import metadata, mapper, Session, engine
from ckan.model.types import make_uuid
from ckan.model.domain_object import DomainObject

get_action = logic.get_action
parse_params = logic.parse_params
redirect = base.redirect
NotFound = logic.NotFound

log = logging.getLogger(__name__)

tess_workflow_table = None


class WorkflowPlugin(plugins.SingletonPlugin, DefaultGroupForm):
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.ITemplateHelpers, inherit=True)
    plugins.implements(plugins.interfaces.IMapper, inherit=True)
    plugins.implements(plugins.IConfigurer, inherit=True)

    def get_helpers(self):
        return {
            'read_workflow_file' : read_workflow_file
        }

    def before_map(self, map):
        map.connect('workflow', '/workflow', controller='ckanext.tess.workflow:WorkflowController', action='index')
        map.connect('new-workflow', '/workflow/new', controller='ckanext.tess.workflow:WorkflowController', action='new')
        map.connect('edit-workflow', '/workflow/edit/{id}', controller='ckanext.tess.workflow:WorkflowController', action='edit')
        # map.connect('read-workflow', '/workflow/{id}', controller='ckanext.tess.workflow:WorkflowController', action='read')
        map.connect('save-workflow', '/workflow/save', controller='ckanext.tess.workflow:WorkflowController', action='save')
        map.connect('delete-workflow', '/workflow/delete/{id}', controller='ckanext.tess.workflow:WorkflowController', action='delete')
        return map


class WorkflowController(HomeController):

    def index(self):
        return base.render('workflow/index.html')

    def new(self):
        return base.render('workflow/new.html')

    def read(self):
        return base.render('workflow/read.html')

    def delete(self):
        self.purge()

    def save(self):
        return base.render('workflow/read.html')


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


# Workflow model
class TessWorkflows(TessDomainObject):
    pass


# Setup the workflow table/model in the DB
def setup():
    log.debug("Setting up workflow model ...")
    if tess_workflow_table is None:
        define_workflow_table()

        if not tess_workflow_table.exists():
            log.debug("Creating workflows table.")
            tess_workflow_table.create()


def define_workflow_table():
    global tess_workflow_table

    tess_workflow_table = Table('tess_workflow', metadata,
                             Column('id',types.UnicodeText, primary_key=True, default=make_uuid),
                             Column('name',types.UnicodeText, default=u''),
                             Column('description',types.UnicodeText, default=u''),
                             Column('definition', types.UnicodeText, default=u'') # workflow definition in JSON format
                             )
    mapper(TessWorkflows,tess_workflow_table)


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