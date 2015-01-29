'''plugin.py

'''
import ckan.plugins.toolkit as toolkit
import ckan.plugins as plugins
import os

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
    data = "<p>No news found!</p>"
  return plugins.toolkit.literal(data)

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
        #toolkit.add_template_directory(config, 'templates')
	    #toolkit.add_public_directory(config, 'public')

        here = os.path.dirname(__file__)
        rootdir = os.path.dirname(os.path.dirname(here))
        our_public_dir = os.path.join(rootdir, 'ckanext',
                                      'tess', 'public')
        template_dir = os.path.join(rootdir, 'ckanext',
                                    'tess', 'templates')
        # set our local template and resource overrides
        config['extra_public_paths'] = ','.join([our_public_dir,
                config.get('extra_public_paths', '')])
        config['extra_template_paths'] = ','.join([template_dir,
                config.get('extra_template_paths', '')])

    	# set the title
        config['ckan.site_title'] = "TeSS Demo"

    	# set the logo
    	config['ckan.site_logo'] = 'images/TeSSLogo.png'

	    #config['ckan.template_head_end'] = config.get('ckan.template_head_end', '') +\
        #                '<link rel="stylesheet" href="/css/tess.css" type="text/css"> '

    def before_map(self, map):
        map.connect('nodes', '/nodes', controller='ckanext.tess.controller:SpecialRouteController', action='nodes')
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
