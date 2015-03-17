import ckan.controllers.group as group
import ckan.plugins.toolkit as toolkit
import ckan.plugins as plugins
from pylons import c
import ckan.lib.helpers as h
import os
import operator
from ckan.lib.plugins import DefaultOrganizationForm


class OrganizationPlugin(plugins.SingletonPlugin, DefaultOrganizationForm):
    plugins.implements(plugins.IGroupForm, inherit=True)

    def group_types(self):
        return ['organization']

    def is_fallback(self):
        return True

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
        schema = super(OrganizationPlugin, self).form_to_db_schema_api_create()
        schema = self._modify_group_schema(schema)
        return schema

    def form_to_db_schema_api_update(self):
        schema = super(OrganizationPlugin, self).form_to_db_schema_api_update()
        schema = self._modify_group_schema(schema)
        return schema

    def form_to_db_schema(self):
        schema = super(OrganizationPlugin, self).form_to_db_schema()
        schema = self._modify_group_schema(schema)
        return schema

    def _modify_group_schema(self, schema):
         #Import core converters and validators
        _convert_to_extras = toolkit.get_converter('convert_to_extras')
        _ignore_missing = toolkit.get_validator('ignore_missing')

        default_validators = [_ignore_missing, _convert_to_extras]
        schema.update({
            'node_id': default_validators,
            'homepage': default_validators
        })
        return schema

    def db_to_form_schema(self):
        # Import core converters and validators
        _convert_from_extras = toolkit.get_converter('convert_from_extras')
        _ignore_missing = toolkit.get_validator('ignore_missing')
        _not_empty = toolkit.get_validator('not_empty')

        schema = super(OrganizationPlugin, self).form_to_db_schema()

        default_validators = [_convert_from_extras, _ignore_missing]
        schema.update({
            'node_id': default_validators,
            'homepage': default_validators
        })
        return schema


import ckan.controllers.organization as organization

class OrganizationController(organization.OrganizationController):
    group_type = 'organization'

    def _guess_group_type(self, expecting_name=False):
        return 'organization'
