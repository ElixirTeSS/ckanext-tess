'''plugin.py

'''
import json as json
import ckan.plugins.toolkit as toolkit
import ckan.plugins as plugins
import ckan.lib.helpers as h
import os
import operator
import urllib2
import urllib
from ckan.common import OrderedDict, c, g, request, _
from ckan.lib.plugins import DefaultGroupForm
import xml.etree.ElementTree as et
import pylons.config as configuration

from dateutil import parser
import datetime
from datetime import timedelta
import ckan.lib.formatters as formatters
from time import gmtime, strftime
from ckanext.tess.model.tables import TessMaterialNode, TessMaterialEvent, TessEvents, TessGroup, TessDomainObject, TessDataset


import ckan.lib.base as base
from ckan.controllers.home import HomeController
import ckan.model as model
import ckan.logic as logic
from urllib import urlencode

get_action = logic.get_action
NotFound = logic.NotFound
ValidationError = logic.ValidationError

import logging

log = logging.getLogger(__name__)

def get_tess_version():
    '''Return the value of 'version' parameter from the setyp.py config file.
    :rtype: string

        '''
    return configuration.get('ckanext.tess.version', 'N/A')


# #Override for the default resource_create code when creating package/dataset
# def tess_resource_create(context, data_dict):
#     import ckan.logic as logic
#     print "here"
#     context['schema'] = TeSSPlugin().create_package_schema()
#     print 'new schema', context['schema']
#     return logic.action.create.resource_create(context, data_dict)

######################
# Plugin starts here #
######################

class TeSSPlugin(plugins.SingletonPlugin):
    '''TeSS CKAN plugin. '''
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.IMapper, inherit=True)
    plugins.implements(plugins.IConfigurer, inherit=True)
    plugins.implements(plugins.ITemplateHelpers, inherit=True)


    def update_config(self, config):
        # Add this plugin's templates dir to CKAN's extra_template_paths, so
        # that CKAN will use this plugin's custom templates.
        # 'templates' is the path to the templates dir, relative to this
        # plugin.py file.
        toolkit.add_template_directory(config, 'templates')
        toolkit.add_public_directory(config, 'public')
        toolkit.add_resource('fantastic', 'tess')

        # set the title
        config['ckan.site_title'] = "TeSS Training Portal"

        # set the logo
        config['ckan.site_logo'] = 'images/ELIXIR_TeSS_logo_white-small.png'

        config['ckanext.tess.version'] = '0.9.1-alpha'

        config['ckan.favicon'] = 'http://www.elixir-europe.org/sites/all/themes/elixir/images/favicons/favicon.ico'
        #config['ckan.template_head_end'] = config.get('ckan.template_head_end', '') +\
        #                '<link rel="stylesheet" href="/css/tess.css" type="text/css"> '

    def after_map(self, map):
        map.connect('report_event', '/event/new', controller='ckanext.tess.plugin:TeSSController', action='report_event')
        # Overrides some routes with a different icon - same alias / url / controller / action.
        map.connect('dataset_groups', '/dataset/groups/{id}', controller='group', action='groups', ckan_icon='folder-open')
        map.connect('dataset_read', '/dataset/{id}', controller='package', action='read', ckan_icon='book')

        map.connect('organization_read', '/organization/{id}', controller='organization', action='read', ckan_icon='book')

        map.connect('group_read', '/group/{id}', controller='group', action='read', ckan_icon='book')

        map.connect('user_dashboard_groups', '/dashboard/groups', controller='user', action='dashboard_groups', ckan_icon='folder-open')
        map.connect('user_dashboard_datasets', '/dashboard/datasets', controller='user',action='dashboard_datasets', ckan_icon='book')
        map.connect('user_datasets', '/user/{id:.*}', controller='user', action='read', ckan_icon='book')

        map.connect('organization_bulk_process','/organization/bulk_process/{id}', controller='organization', action='bulk_process', ckan_icon='book')
        return map

    def get_helpers(self):
        return {
            'get_tess_version': get_tess_version
        }