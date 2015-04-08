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
from time import gmtime, strftime

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


def parse_xml(xml):
    doc = et.fromstring(xml)
    result_element = doc.find('result')
    count = 0
    try:
        count = int(result_element.attrib.get('numFound'))
    except Exception, e:
        print 'Could not load result element'

    docs = doc.findall('*/doc')
    results = []
    for doc in docs:
        res = {'title': doc.find("*/[@name='title']").text,
               'provider': doc.find("*/[@name='provider']").text,
               'id': doc.find("*/[@name='id']").text,
               'link': doc.find("*/[@name='link']").text,
               'subtitle': doc.find("*/[@name='subtitle']").text,
               'venue': doc.find("*/[@name='venue']").text,
               'country': doc.find("*/[@name='country']").text,
               'city': doc.find("*/[@name='city']").text,
               'start': doc.find("*/[@name='start']").text
               }
        results.append(res)
    return {'count': count, 'events': results}


def construct_url(parameter):
    try:
        category = parameter.get('category', None)
        rows = parameter.get('rows', None)
        q = parameter.get('q', None)

        original_url = 'http://iann.pro/solr/select/?'
        if not rows:
            rows = 100
        original_url = ('%srows=%s' % (original_url, rows))

        if category:
            original_url = ('%s&q=category:%s' % (original_url, category))
        else:
            original_url = ('%s&q=category:%s' % (original_url, 'course'))
        print original_url
        if q:
            split = q.replace(' ', '","')
            title = ('title:("%s","%s")' % (urllib.quote(q), split))
            keywords = ('keyword:("%s")' % split)
            parameters = ('%s OR %s' % (title, keywords))
            if False:  # Exclude this for past events too
                today = strftime('%Y-%m-%dT00-00-00Z', gmtime())
                date = ('start:[%s TO *]' % (today))
                parameters = ('%s AND (%s)' % (parameters, date))
            url = ("%s%%20AND%%20%s" % (original_url, urllib.quote(parameters)))
        else:
            url = original_url
        return url
    except Exception, e:
        print 'Failed to construct URL for iAnn API \n %s' % e


def events(parameter=None):
    results = {}
    url = construct_url(parameter)
    try:
        res = urllib2.urlopen(url)
        res = res.read()
        results = parse_xml(res)
        results['url'] = url
    except Exception, e:
        print 'Error loading events from iANN.pro: \n %s' % e
    return results


def related_events(model):
    try:
        name = model.get('title', None)
        return events(name)
    except Exception, e:
        print 'Model has no title attribute: \n %s' % e
        return None


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
        config['ckan.site_logo'] = 'images/ELIXIR_TeSS_logo-small.png'

        #config['ckan.template_head_end'] = config.get('ckan.template_head_end', '') +\
        #                '<link rel="stylesheet" href="/css/tess.css" type="text/css"> '

    def before_map(self, map):
        map.connect('node_old', '/node_old', controller='ckanext.tess.plugin:TeSSController', action='node_old')
        map.connect('workflow', '/workflow', controller='ckanext.tess.plugin:TeSSController', action='workflows')
        map.connect('event', '/event', controller='ckanext.tess.plugin:TeSSController', action='events')
        map.connect('dataset_events', '/dataset/events/{id}', controller='ckanext.tess.plugin:TeSSController', action='add_events')
        return map

    def dataset_facets(self, facets_dict, package_type):
        facets_dict['node_id'] = 'ELIXIR Nodes'
        return facets_dict

    def setup_template_variables(self, context, data_dict):
        c.filterable_nodes = 'HI'

    def get_helpers(self):
        return {
                'read_news_iann': iann_news,
                'related_events': related_events,
                'events': events
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


import ckan.lib.base as base
from ckan.controllers.home import HomeController
import ckan.model as model
import ckan.logic as logic
get_action = logic.get_action



class TeSSController(HomeController):
    def node_old(self):
        return base.render('node_old/index.html')

    def events(self):
        q_params = {}
        q_params['q'] = c.q = request.params.get('q', '')
        q_params['category'] = request.params.get('category', '')
        q_params['rows'] = request.params.get('rows', '')

        events_hash = events(q_params)
        c.events = events_hash.get('events')
        c.events_count = events_hash.get('count')
        c.events_url = events_hash.get('url')

        return base.render('event/read.html')

    def workflows(self):
        return base.render('workflow/index.html')

    def add_events(self, id):
        context = {'model': model, 'session': model.Session,
                   'api_version': 3, 'for_edit': True,
                   'user': c.user or c.author, 'auth_user_obj': c.userobj}
        pkg_dict = get_action('package_show')(context, {'id': id})
        c.pkg_dict = pkg_dict
        events_hash = related_events(pkg_dict)
        if events_hash:
            c.events = events_hash.get('events')
            c.events_count = events_hash.get('count')
            c.events_url = events_hash.get('url')

        return base.render('package/related_events.html', extra_vars={'pkg': pkg_dict})