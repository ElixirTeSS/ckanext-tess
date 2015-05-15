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
from ckanext.tessrelations.model.tables import TessMaterialNode, TessMaterialEvent, TessEvents, TessGroup, TessDomainObject, TessDataset

import ckan.lib.base as base
from ckan.controllers.home import HomeController
import ckan.model as model
import ckan.logic as logic
from urllib import urlencode

get_action = logic.get_action
NotFound = logic.NotFound
ValidationError = logic.ValidationError


def get_tess_version():
    '''Return the value of 'version' parameter from the setyp.py config file.
    :rtype: string

        '''
    return configuration.get('ckanext.tess.version', 'N/A')

# Return the iann specific news. This could be replaced with a general news function taking
# the news source as an argument.
def iann_news():
  try:
    with open ("/tmp/iann.txt", "r") as myfile:
      data = myfile.read()
  except Exception, e:
    print "iann_news: " + str(e)
    data = "<p>No events found!</p>"
  return plugins.toolkit.literal(data)


######################
# Plugin starts here #
######################
class TeSSPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    '''TeSS CKAN plugin.

    '''
    # Declare that this class implements IConfigurer.
    #plugins.implements(plugins.IConfigurer)

    plugins.implements(plugins.IConfigurer, inherit=True)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.IDatasetForm, inherit=True)
    plugins.implements(plugins.ITemplateHelpers, inherit=True)
    plugins.implements(plugins.IFacets, inherit=True)

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

        #config['ckan.template_head_end'] = config.get('ckan.template_head_end', '') +\
        #                '<link rel="stylesheet" href="/css/tess.css" type="text/css"> '

    def before_map(self, map):
        map.connect('report_event', '/event/new', controller='ckanext.tess.plugin:TeSSController', action='report_event')
        return map

    def dataset_facets(self, facets_dict, package_type):
        facets_dict['node_id'] = 'ELIXIR Nodes'
        return facets_dict

    def get_helpers(self):
        return {
                'get_tess_version' : get_tess_version,
                'read_news_iann': iann_news
                }

    def _modify_package_schema(self, schema):
        schema.update({
            'node_id': [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_extras')]
        })
        return schema

    def show_package_schema(self):
        schema = super(TeSSPlugin, self).show_package_schema()
        schema['tags']['__extras'].append(toolkit.get_converter('free_tags_only'))
        schema.update({
            'node_id': [
                toolkit.get_converter('convert_from_extras'),
                toolkit.get_validator('ignore_missing')]
        })
        return schema

    def create_package_schema(self):
        schema = super(TeSSPlugin, self).create_package_schema()
        schema = self._modify_package_schema(schema)
        return schema

    def update_package_schema(self):
        schema = super(TeSSPlugin, self).update_package_schema()
        schema = self._modify_package_schema(schema)
        return schema

    def is_fallback(self):
        # Return True to register this plugin as the default handler for
        # package types not handled by any other IDatasetForm plugin.
        return True

    def package_types(self):
        # This plugin doesn't handle any special package types, it just
        # registers itself as the default (above).
        return []




class TeSSController(HomeController):
    def node_old(self):
        return base.render('node_old/index.html')

