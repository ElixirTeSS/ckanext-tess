import ckan.controllers.group as group
import json as json
import ckan.plugins.toolkit as toolkit
import ckan.plugins as plugins
from pylons import c
import ckan.lib.helpers as h
import os
import operator
import ckan.logic as logic
NotFound = logic.NotFound

from ckan.lib.plugins import DefaultGroupForm

class NodePlugin(plugins.SingletonPlugin, DefaultGroupForm):
    plugins.implements(plugins.IGroupForm, inherit=True)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.ITemplateHelpers, inherit=True)
    plugins.implements(plugins.interfaces.IMapper, inherit=True)

    def get_helpers(self):
        return {
                'file_exist':file_exist,
                'get_all_nodes': get_all_nodes,
                'get_all_node_names': get_all_node_names,
                'node_domain': node_domain,
                'key_to_title': key_to_title,
                'get_available_country_codes': get_available_country_codes,
                'get_available_country_names': get_available_country_names,
                'get_country_code_for_name': get_country_code_for_name,
                'get_country_name_for_code': get_country_name_for_code,
                'get_available_countries': get_available_countries,
                'get_extras': get_extras,
                'get_node_materials': node_materials,
                'training_coordinators': training_coordinators,
                'tess_reorder_dataset_facets': reorder_dataset_facets,
                'all_nodes': all_nodes,
                'all_node_name_and_ids': all_node_name_and_ids,
                'all_content_provider_name_and_ids': all_content_provider_name_and_ids,
                'get_node': get_node,
                'display_name_of_node': display_name_of_node,
                'carousel_images_of_node': carousel_images_of_node,
                'country_code_of_node': country_code_of_node,
                'string_to_json_object': string_to_json_object
        }

    def before_map(self, map):
        map.connect('node', '/node', controller='ckanext.tess.node:NodeController', action='index')
        map.connect('new-node', '/node/new', controller='ckanext.tess.node:NodeController', action='new')
        map.connect('edit-node', '/node/edit/{id}', controller='ckanext.tess.node:NodeController', action='edit')
        map.connect('read-node', '/node/{id}', controller='ckanext.tess.node:NodeController', action='read')
        map.connect('delete-node', '/node/delete/{id}', controller='ckanext.tess.node:NodeController', action='delete')
        map.connect('bulk_process_org', '/organization/bulk_process/{id}',
                    controller='ckanext.tess.organization:OrganizationController',
                    action='bulk_process')
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

    def bulk_process_template(self):
        return 'node/bulk_process.html'

    def after_delete(mapper, connection, instance):
        print 'instance deleted: '
        return

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
            'home_page': default_validators,
            'institutions': default_validators, # string in JSON format
            'trc': default_validators,
            'trc_email': default_validators,
            'trc_image': default_validators,
            'staff': default_validators, # in JSON format
            'carousel_image_1': default_validators,
            'carousel_image_2': default_validators,
            'carousel_image_3': default_validators,
            'twitter': default_validators
        })
        return schema

    def db_to_form_schema(self):
        # Import core converters and validators
        _convert_from_extras = toolkit.get_converter('convert_from_extras')
        _ignore_missing = toolkit.get_validator('ignore_missing')
        _not_empty = toolkit.get_validator('not_empty')

        schema = super(NodePlugin, self).form_to_db_schema()

        default_validators = [_convert_from_extras, _ignore_missing]
        schema.update({
            'country_code': default_validators,
            'home_page': default_validators,
            'institutions': default_validators, # string in JSON format
            'trc': default_validators,
            'trc_email': default_validators,
            'trc_image': default_validators,
            'staff': default_validators, # string in JSON format
            'carousel_image_1': default_validators,
            'carousel_image_2': default_validators,
            'carousel_image_3': default_validators,
            'twitter': default_validators
        })
        return schema


class NodeController(group.GroupController):
    group_type = 'node'

    def _guess_group_type(self, expecting_name=False):
        return 'node'




def reorder_dataset_facets(facet_keys, facet_values):
    ''' Helper function that reorders 2 input lists so that
        our 'ELIXIR Nodes' facet/filter (using key 'node_id') is the second in the list (if there are more than 2 facets).
        Input parameters:
        facet_keys is list of facet dictionary keys;
        facet_values is list of facet dictionary values
        Both lists must be of the same length.

    '''
    index = facet_keys.index("node_id") if "node_id" in facet_keys else None
    if (index is not None and index > 1 and len(facet_keys) > 2):
        facet_keys[1], facet_keys[index] = facet_keys[index], facet_keys[1]
        facet_values[1], facet_values[index] = facet_values[index], facet_values[1]
    return facet_keys, facet_values

def node_materials(node):
    datasets = toolkit.get_action("package_search") \
        (data_dict={'fq':'node_id:'+node.get('name'), 'rows':5000
        })
    return datasets['results']

def all_nodes():
    data = {'type': 'node', 'all_fields': True}
    return toolkit.get_action('group_list')({}, data)

def all_content_providers():
    data = {'all_fields': True}
    cps=toolkit.get_action('organization_list')({}, data)
    return cps

#returns something like:   [{'United Kingdom', 'united-kingdom'},
#                         {'EMBL-EBI', 'embl-ebi'}]
# Hmmm, there is an actual id field (immutable) - should we not be using it instead of
# name/slug which can be changed?
def all_node_name_and_ids():
    list = []
    for nodes in all_nodes():
        list.append([nodes.get('display_name'), nodes.get('name'), nodes.get('id')])
    return list

def all_content_provider_name_and_ids():
    list = []
    for content_provider in all_content_providers():
        list.append([content_provider.get('display_name'), content_provider.get('name'), content_provider.get('id')])
    return list

def get_node(node_id):
    try:
        data = {'id': node_id}
        return toolkit.get_action('group_show')({}, data)
    except NotFound:
        return None



def display_name_of_node(node_id):
    node = get_node(node_id)
    if node:
        if node.get('display_name'):
            return node.get('display_name')
        else:
            return node_id.replace('-', ' ').title()
    else:
        return "None"

def carousel_images_of_node(node):
    carousel = [node.get('carousel_image_1'), node.get('carousel_image_2'), node.get('carousel_image_3')]
    carousel = filter(None, carousel)
    return {'length': len(carousel) or 0, 'carousel': carousel}


def country_code_of_node(node_id):
    node = get_node(node_id)
    if node.get('country_code'):
        return node.get('country_code')
    else:
        return node_id

def file_exist(file_name):
    here = os.path.dirname(__file__)
    rootdir = os.path.dirname(os.path.dirname(here))
    template_dir = os.path.join(rootdir, 'ckanext',
                                  'tess', 'templates')
    return os.path.exists(template_dir + "/" + file_name)

def get_all_nodes():
    nodes = toolkit.get_action("group_list")\
        (data_dict={'all_fields': True,
                    'include_extras': True,
                    'type': 'node', 'for_view': True})
    return nodes


def training_coordinators():
    node_names = get_all_node_names()
    trcs = []
    for node_name in node_names:
        node = get_node(node_name)
        trc = node.get('trc', None)
        if trc:
            trcs.append({'trc': trc,
                         'trc_email': node.get('trc_email'),
                         'trc_image': node.get('trc_image'),
                         'node': node})
    return trcs


def get_all_node_names():
    nodes = toolkit.get_action("group_list")\
        (data_dict={'all_fields': False,
                    'include_extras': False,
                    'type': 'node'})
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
        # json file containing country code -> country name map for member and observer countries
        file = os.path.join(here,'countries-elixir.json')
        with open(file) as data_file:
            try:
                countries_map = json.load(data_file)['members']
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
    :return: A list of available country codes not yet taken up by ELIXIR node_old
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
    :return: A list of available country codes not yet taken up by ELIXIR node_old
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
            available_country_names.append({'text': country_name,
                                            'value': country_name})
            available_country_names.append(country_name)
    return available_country_names

def get_available_countries():
    '''
    :return: A list of dictionaries {'text': country_name, 'value': country_code_for node, 'name': country_name} of countries
    that have not already been taken by existing node_old.
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

def string_to_json_object(str):
    if not str:
        return None
    else:
        try:
            obj = json.loads(str)
            return obj
        except Exception, e:
            print 'Failed to convert string to JSON object: ' + str
            print e
            return None
