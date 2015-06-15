import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

import ckan.lib.helpers as h
from ckan.common import c

class PackagePlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):

    plugins.implements(plugins.IDatasetForm, inherit=False)
    plugins.implements(plugins.ITemplateHelpers, inherit=False)
    events = 'KEMOOOON'

    def after_map(self, map):
        map.connect('user_datasets', '/user/{id:.*}', controller='user', action='read', ckan_icon='book')
        map.connect('dataset_read', '/dataset/{id}', controller='package', action='read', ckan_icon='book')

    def dataset_facets(self, facets_dict, package_type):
        facets_dict['node_id'] = 'ELIXIR Nodes'
        return facets_dict

    def _modify_package_schema(self, schema):
        c.events = {'blah': 'blah'}
        _convert_to_extras = toolkit.get_converter('convert_to_extras')
        _ignore_missing = toolkit.get_validator('ignore_missing')
        _not_empty = toolkit.get_validator('not_empty')
        _not_missing = toolkit.get_validator('not_missing')
        _url_validator = toolkit.get_validator('url_validator')

        schema.update({
            'node_id': [_ignore_missing, _convert_to_extras],
            'url': [_not_empty, _url_validator],
            'notes': [_not_empty, _not_missing]
        })
        schema['resources'].update({ 'image_url' : [ _convert_to_extras, _ignore_missing, _url_validator ] })
        return schema

    def get_helpers(self):
        return {}

    def show_package_schema(self):
        c.events = {'blah': 'blah'}
        schema = super(PackagePlugin, self).show_package_schema()

        schema['tags']['__extras'].append(toolkit.get_converter('free_tags_only'))

        _convert_from_extras = toolkit.get_converter('convert_from_extras')
        _ignore_missing = toolkit.get_validator('ignore_missing')
        _not_empty = toolkit.get_validator('not_empty')
        _not_missing = toolkit.get_validator('not_missing')
        _url_validator = toolkit.get_validator('url_validator')

        schema.update({
            'node_id': [_convert_from_extras, _ignore_missing],
            'url': [_not_empty, _url_validator],
            'notes': [_not_empty, _not_missing]
        })
        schema['resources'].update({ 'image_url' : [ _convert_from_extras, _ignore_missing, _url_validator ] })
        return schema

    def create_package_schema(self):
        schema = super(PackagePlugin, self).create_package_schema()
        schema = self._modify_package_schema(schema)
        return schema

    def update_package_schema(self):
        schema = super(PackagePlugin, self).update_package_schema()
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

    def setup_template_variables(self, context, data_dict):
        print 'does anyone ever listen to me '
        PackagePlugin.events = {'blah': 'blah'}
        return super(PackagePlugin, self).setup_template_variables(
                context, data_dict)