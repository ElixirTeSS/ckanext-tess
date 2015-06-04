__author__ = 'milo'


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

log = logging.getLogger(__name__)

material_event_table = None
material_node_table = None
tess_event_table = None

def setup():
    log.debug("In the setup...")
    if material_event_table is None:
        define_tables()

        if not tess_event_table.exists():
            log.debug("Creating events table.")
            tess_event_table.create()

        if not material_event_table.exists():
           log.debug("Creating material <-> event table.")
           material_event_table.create()

        if not material_node_table.exists():
            log.debug("Creating material <-> node table.")
            material_node_table.create()

        if not tess_workflow_table.exists():
            log.debug("Creating workflows table.")
            tess_workflow_table.create()




def define_tables():
    log.debug("Defining tables")
    global material_event_table
    global material_node_table
    global tess_event_table
    global tess_dataset_table
    global tess_group_table
    global tess_workflow_table

    # Attempt to gain access to the group table
    tess_group_table = Table('group',metadata,extend_existing=True)
    mapper(TessGroup, tess_group_table)

    tess_dataset_table = Table('package',metadata,extend_existing=True)
    mapper(TessDataset, tess_dataset_table)

    tess_workflow_table = Table('tess_workflow', metadata,
                             Column('id',types.UnicodeText, primary_key=True, default=make_uuid),
                             Column('name',types.UnicodeText, default=u''),
                             Column('description', types.UnicodeText, default=u''),
                             Column('definition', types.UnicodeText, default=u''), # workflow definition in JSON format
                             Column('creator_user_id', types.UnicodeText, default=u''),
                             Column('created', types.DateTime, default=datetime.datetime.utcnow),
                             Column('last_modified', types.DateTime, default=datetime.datetime.utcnow)
                            )

    mapper(TessWorkflow,tess_workflow_table)

    # First attempt at events, with minimal information.
    tess_event_table = Table('tess_events', metadata,
                             Column('id',types.UnicodeText, primary_key=True),
                             Column('title', types.UnicodeText, default=u''),
                             Column('provider', types.UnicodeText, default=u''),
                             Column('link', types.UnicodeText, default=u''),
                             Column('subtitle', types.UnicodeText, default=u''),
                             Column('venue', types.UnicodeText, default=u''),
                             Column('country', types.UnicodeText, default=u''),
                             Column('city', types.UnicodeText, default=u''),
                             Column('starts', types.UnicodeText, default=u''),
                             Column('ends', types.UnicodeText, default=u''),
                             Column('duration', types.UnicodeText, default=u'')
                            )

    mapper(TessEvents,tess_event_table)

    material_event_table = Table('material_event', metadata,
                                Column('id',types.UnicodeText, primary_key=True, default=make_uuid),
                                Column('material_id', types.UnicodeText, ForeignKey('package.id')),
                                Column('event_id', types.UnicodeText),
                            )
    # ForeignKey('harvest_object.id')

    mapper(TessMaterialEvent, material_event_table)

    material_node_table = Table('material_node', metadata,
                                Column('id',types.UnicodeText, primary_key=True, default=make_uuid),
                                Column('material_id', types.UnicodeText, ForeignKey('package.id')),
                                Column('node_id', types.UnicodeText, ForeignKey('group.id')),
                            )

    mapper(TessMaterialNode, material_node_table)





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
class TessWorkflow(TessDomainObject):
    pass

class TessMaterialEvent(TessDomainObject):
    pass

class TessMaterialNode(TessDomainObject):
    pass

# Group table with group type set to 'node'
class TessGroup(TessDomainObject):
    pass

# Event table
class TessEvents(TessDomainObject):
    pass

# Datasets, i.e. training materials
class TessDataset(TessDomainObject):
    pass


