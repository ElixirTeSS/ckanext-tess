import logging
import os
import ckan.plugins as plugins
import ckan.plugins.toolkit as tk
from ckan.lib.plugins import DefaultGroupForm


class NodePlugin(plugins.SingletonPlugin,DefaultGroupForm):

    plugins.implements(plugins.IConfigurer, inherit=True)
    plugins.implements(plugins.IGroupForm, inherit=True)
    plugins.implements(plugins.IRoutes, inherit=True)

    def before_map(self, map):
        map.connect('/node', controller='ckanext.tess.controller:NodeController', action='index')
        map.connect('/node/new', controller='ckanext.tess.controller:NodeController', action='new')
        map.connect('/node/edit/{id}', controller='ckanext.tess.controller:NodeController', action='edit')
        map.connect('/node/{id}', controller='ckanext.tess.controller:NodeController', action='read')
        return map

    def after_map(self, map):
        return map

    def update_config(self, config):
        tk.add_template_directory(config, 'templates')

    def group_form(self):
        return 'node/new_node_form.html'

    def new_template(self):
        return 'node/new.html'

    def about_template(self):
        return 'node/about.html'

    def index_template(self):
        print '============+CAllling node.py index_template method'
        return 'node/index.html'

    def admins_template(self):
        return 'node/admins.html'

    def bulk_process_template(self):
        return 'node/bulk_process.html'

    # don't override history_template - use group template for history

    def edit_template(self):
        return 'node/edit.html'

    def activity_template(self):
        return 'node/activity_stream.html'

    def is_fallback(self):
        # Return True to register this plugin as the default handler for
        # package types not handled by any other IDatasetForm plugin.
        return False

    def group_types(self):
        # This plugin doesn't handle any special package types, it just
        # registers itself as the default (above).
        return ['node']

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
        _convert_to_extras = tk.get_converter('convert_to_extras')
        _ignore_missing = tk.get_validator('ignore_missing')


        default_validators = [_ignore_missing, _convert_to_extras]
        schema.update({
                       'project_leader':default_validators
                       })
        return schema

    def db_to_form_schema(self):

        # Import core converters and validators
        _convert_from_extras = tk.get_converter('convert_from_extras')
        _ignore_missing = tk.get_validator('ignore_missing')
        _not_empty = tk.get_validator('not_empty')

        schema = super(IgroupformExample, self).form_to_db_schema()

        default_validators = [_convert_from_extras, _ignore_missing]
        schema.update({
                        'project_leader':default_validators,
                        'num_followers': [_not_empty],
                        'package_count': [_not_empty],
                       })
        return schema
