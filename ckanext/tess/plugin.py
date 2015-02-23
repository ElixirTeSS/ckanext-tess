'''plugin.py

'''
import json as json
import ckan.plugins.toolkit as toolkit
import ckan.plugins as plugins
import ckan.lib.helpers as h
import os
import operator

from ckan.lib.plugins import DefaultGroupForm

def node_list():
    return elixir_nodes()

def node_materials(node):
    datasets = toolkit.get_action("package_search")(
        data_dict={'fq':node, 'facet.field':['elixir_nodes']})
    if (datasets['count'] > 0):
        return datasets['results']
    else:
        return None

def node_organizations(node):
    return None

def elixir_nodes():
    create_elixir_nodes()

    try:
        tag_list = toolkit.get_action('tag_list')
        elixir_nodes = tag_list(data_dict={'vocabulary_id': 'elixir_nodes'})
        return elixir_nodes
    except toolkit.ObjectNotFound:
        return None

def create_elixir_nodes():
    user = toolkit.get_action('get_site_user')({'ignore_auth': True}, {})
    context = {'user': user['name']}
    try:
       data = {'id': 'elixir_nodes'}
       toolkit.get_action('vocabulary_show')(context, data)
    except toolkit.ObjectNotFound:
       data = {'name': 'elixir_nodes'}
       vocab = toolkit.get_action('vocabulary_create')(context, data)
       for tag in (u'United Kingdom', u'Netherlands', u'Switzerland', u'Sweden', u'Finland',
                   u'Portugal', u'Estonia', u'Israel', u'Norway', u'Denmark', u'EBI', 'Czech Republic',
                   u'Belgium', u'Slovenia', u'France', u'Greece', u'Italy', u'Spain'):
           data = {'name': tag, 'vocabulary_id': vocab['id']}
           toolkit.get_action('tag_create')(context, data)

def reorder_dataset_facets(facet_keys, facet_values):
    ''' Helper function that reorders 2 input lists so that
        our 'ELIXIR Nodes' facet/filter (using key 'vocab_elixir_nodes') is the second in the list (if there are more than 2 facets).
        Input parameters:
        facet_keys is list of facet dictionary keys;
        facet_values is list of facet dictionary values
        Both lists must be of the same length.

    '''
    index = facet_keys.index("vocab_elixir_nodes") if "vocab_elixir_nodes" in facet_keys else None
    if (index is not None and index > 1 and len(facet_keys) > 2):
        facet_keys[1], facet_keys[index] = facet_keys[index], facet_keys[1]
        facet_values[1], facet_values[index] = facet_values[index], facet_values[1]
    return facet_keys, facet_values

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
        config['ckan.site_title'] = "TeSS Portal"

        # set the logo
    	config['ckan.site_logo'] = 'images/TeSSLogo-small.png'

        #config['ckan.template_head_end'] = config.get('ckan.template_head_end', '') +\
        #                '<link rel="stylesheet" href="/css/tess.css" type="text/css"> '

    def before_map(self, map):
        map.connect('workflows', '/workflows', controller='ckanext.tess.controller:SpecialRouteController', action='workflows')
        map.connect('events', '/events', controller='ckanext.tess.controller:SpecialRouteController', action='events')
        return map

    def dataset_facets(self, facets_dict, package_type):
        facets_dict['vocab_elixir_nodes'] = plugins.toolkit._('ELIXIR Nodes')
        return facets_dict

    def get_helpers(self):
        return {'elixir_nodes': elixir_nodes,
                'get_node_list': node_list,
                'get_node_materials': node_materials,
                'get_node_organizations': node_organizations,
                'tess_elixir_nodes': elixir_nodes, 'tess_reorder_dataset_facets': reorder_dataset_facets,
                'read_news_iann': iann_news
                }

    def _modify_package_schema(self, schema):
        schema.update({
            'custom_text': [toolkit.get_validator('ignore_missing'),
                            toolkit.get_converter('convert_to_extras')]
        })
        schema.update({
            'elixir_node': [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_tags')('elixir_nodes')
            ]
        })
        return schema

    def show_package_schema(self):
        schema = super(TeSSPlugin, self).show_package_schema()
        schema.update({
            'custom_text': [toolkit.get_converter('convert_from_extras'),
                            toolkit.get_validator('ignore_missing')]
        })

        schema['tags']['__extras'].append(toolkit.get_converter('free_tags_only'))
        schema.update({
            'elixir_node': [
                toolkit.get_converter('convert_from_tags')('elixir_nodes'),
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

def file_exist(file_name):
    here = os.path.dirname(__file__)
    rootdir = os.path.dirname(os.path.dirname(here))
    template_dir = os.path.join(rootdir, 'ckanext',
                                  'tess', 'templates')
    return os.path.exists(template_dir + "/" + file_name)

def get_all_nodes():
    nodes = toolkit.get_action("group_list")(data_dict={'all_fields':True, 'include_extras':True, 'type':'node'})
    return nodes

def node_domain():
    return 'http://127.0.0.1:5000/node'

def key_to_title(key):
    lookup = { 'trc': 'Training coordinator',
                     'tec': 'Technical coordinator',
                     'hon': 'Head of node',
                     'country_code': 'Country code',
                     'country_name': 'Country name'}
    return lookup.get(key)

# Global variable to hold country code -> country name map
countries_map = None
# Global variable to hold country name -> country code map
transposed_countries_map = None

def get_countries_map():
    '''
    :return: A country code -> country name map
    '''
    global countries_map # uses global variable
    if countries_map is None:
        here = os.path.dirname(__file__)
        # json file containing country code -> country name map
        file = os.path.join(here,'countries-for-elixir.json')
        with open(file) as data_file:
            try:
                countries_map = json.load(data_file)
            except Exception, e:
                print e
                countries_map = {}
    return countries_map

def get_transposed_countries_map():
    '''
    :return: A country name -> country code map
    '''
    global transposed_countries_map # uses global variable
    if transposed_countries_map is None:
        countries_map = get_countries_map() # local variable
        transposed_countries_map = {v: k for k, v in countries_map.items()}
    return transposed_countries_map

def get_country_name_for_code(country_code):
    '''
    :param country_code:
    :return: The name of a country given its country code.
    '''
    if country_code is None or country_code.strip() == "":
        return ""
    countries_map = get_countries_map() # country code -> country name hash
    return countries_map[country_code]

def get_country_code_for_name(country_name):
    '''
    :param country_name:
    :return: The code of a country given its name.
    '''
    print 'country name ', country_name
    if country_name is None or country_name.strip() == "":
        return ""
    transposed_countries_map = get_transposed_countries_map() # country name -> country code hash
    print 'transposed_countries_map', transposed_countries_map
    return transposed_countries_map[country_name]

def get_available_country_codes():
    '''
    :return: A list of available country codes not yet taken up by ELIXIR nodes
    '''
    countries_map = get_countries_map() # country code -> country name hash
    nodes = get_all_nodes()
    country_codes_in_use = []
    for node in nodes:
        try:
            extras = node.get('extras')
            country_codes_in_use.append(extras['key' == 'country_code'].get('value', None))
        except Exception, e:
            print e
            country_codes_in_use
    available_country_codes = []
    for country_code in countries_map.keys():
        if not country_code in country_code_in_use:
             #output in format - [{'name':2010, 'value': 2010},{'name': 2011, 'value': 2011}]
             #to use the form macro form.select(...).
            display_name = country_code + ' (' + countries_map.get(country_code) + ')'
            available_country_codes.append({'text':display_name, 'value':country_code})
    return available_country_codes

def get_available_country_names():
    '''
    :return: A list of available country codes not yet taken up by ELIXIR nodes
    '''
    countries_map = get_countries_map()
    nodes = get_all_nodes()
    country_names_in_use = []
    for node in nodes:
        country_names_in_use.append(node['title'])
    available_country_names = []
    for country_name in countries_map.values():
        if not country_name in country_names_in_use:
             #output in format - [{'name':2010, 'value': 2010},{'name': 2011, 'value': 2011}]
             #to use the form macro form.select(...).
            available_country_names.append({'text':country_name, 'value':country_name})
            available_country_names.append(country_name)
    return available_country_names

def get_available_countries():
    '''
    :return: A list of dictionaries {'text': country_name, 'value': country_code_for node, 'name': country_name} of countries
    that have not already been taken by existing nodes.
    '''
    countries = get_countries_map()
    nodes = get_all_nodes()
    country_codes_in_use = []
    for node in nodes:
        try:
            extras = node.get('extras')
            country_codes_in_use.append(extras['key' == 'country_code'].get('value', None))
        except Exception, e:
            print e
            country_codes_in_use
    available_countries = []
    for country_code in countries.keys():
        if not country_code in country_codes_in_use:
             #output in format - [{'name':2010, 'value': 2010},{'name': 2011, 'value': 2011}]
             #to use the form macro form.select(...).
            display_name = countries.get(country_code)
            available_countries.append({'text':display_name, 'value':country_code, 'name':display_name})
    available_countries.sort(key=lambda x: x['name']) #sort the list based on country name
    return available_countries

def get_extras(node):
    extras = node.get('extras')
    if extras is not None:
        for extra in extras:
            node[extra['key']] = extra['value']
    return node


class NodePlugin(plugins.SingletonPlugin, DefaultGroupForm):
    plugins.implements(plugins.IGroupForm, inherit=True)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.ITemplateHelpers, inherit=True)

    def get_helpers(self):
        return {
                'file_exist':file_exist,
                'get_all_nodes': get_all_nodes,
                'node_domain': node_domain,
                'key_to_title': key_to_title,
                'get_available_country_codes': get_available_country_codes,
                'get_available_country_names': get_available_country_names,
                'get_country_code_for_name': get_country_code_for_name,
                'get_country_name_for_code': get_country_name_for_code,
                'get_available_countries': get_available_countries,
                'get_extras': get_extras,
        }

    def before_map(self, map):
        map.connect('node', '/node', controller='ckanext.tess.controller:NodeController', action='index')
        map.connect('new-node', '/node/new', controller='ckanext.tess.controller:NodeController', action='new')
        map.connect('edit-node', '/node/edit/{id}', controller='ckanext.tess.controller:NodeController', action='edit')
        map.connect('read-node', '/node/{id}', controller='ckanext.tess.controller:NodeController', action='read')
        return map

    def after_map(self, map):
        return map

    def is_fallback(self):
        return False

    def group_types(self):
        return ['node']

    def group_form(self):
        return 'node/new_node_form.html'

    def new_template(self):
        return 'node/new.html'

    def read_template(self):
        return 'node/read.html'

    def index_template(self):
        return 'node/index.html'

    def edit_template(self):
        return 'node/edit.html'

    def form_to_db_schema_options(self, options):
        ''' This allows us to select different schemas for different
        purpose eg via the web interface or via the api or creation vs
        updating. It is optional and if not available form_to_db_schema
        should be used.
        If a context is provided, and it contains a schema, it will be
        returned.
        '''
        schema = options.get('context', {}).get('schema', None)
        if schema:
            return schema

        if options.get('api'):
            if options.get('type') == 'create':
                return self.form_to_db_schema_api_create()
            else:
                return self.form_to_db_schema_api_update()
        else:
            return self.form_to_db_schema()

    def form_to_db_schema_api_create(self):
        schema = super(NodePlugin, self).form_to_db_schema_api_create()
        schema = self._modify_group_schema(schema)
        return schema

    def form_to_db_schema_api_update(self):
        schema = super(NodePlugin, self).form_to_db_schema_api_update()
        schema = self._modify_group_schema(schema)
        return schema

    def form_to_db_schema(self):
        schema = super(NodePlugin, self).form_to_db_schema()
        schema = self._modify_group_schema(schema)
        return schema

    def _modify_group_schema(self, schema):
         #Import core converters and validators
        _convert_to_extras = toolkit.get_converter('convert_to_extras')
        _ignore_missing = toolkit.get_validator('ignore_missing')


        default_validators = [_ignore_missing, _convert_to_extras]
        schema.update({
                       'country_code': [_convert_to_extras],
                       'hon':default_validators,
                       'tec':default_validators,
                       'trc':default_validators
                       })
        return schema

    def db_to_form_schema(self):
        print 'updating schema'
        # Import core converters and validators
        _convert_from_extras = toolkit.get_converter('convert_from_extras')
        _ignore_missing = toolkit.get_validator('ignore_missing')
        _not_empty = toolkit.get_validator('not_empty')

        schema = super(NodePlugin, self).form_to_db_schema()

        default_validators = [_convert_from_extras, _ignore_missing]
        schema.update({
                       'country_code':default_validators,
                       'hon':default_validators,
                       'tec':default_validators,
                       'trc':default_validators
                       })
        return schema