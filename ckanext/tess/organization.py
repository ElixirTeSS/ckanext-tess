import ckan.controllers.group as group
import ckan.plugins.toolkit as toolkit
import ckan.plugins as plugins
from pylons import c
import ckan.lib.helpers as h
import os
import operator
from ckan.common import OrderedDict, c, g, request, _
from ckan.lib.plugins import DefaultOrganizationForm
import ckan.logic as logic
import ckan.model as model

import ckan.lib.base as base
render = base.render
redirect = base.redirect
get_action = logic.get_action
parse_params = logic.parse_params

# Node is internal name - e.g. united-kingdom
# The params are dataset_id as key and previous node-code as value
# For example:
# params = {'dataset_392jekf93u93j39fes239': 'GB',
#           'dataset_a3ij3jmdsijfdsion393u': 'ES'
# }


def update_node_of_materials(node, params):
    count = 0
    for param in params:
        if param.startswith('dataset_'):
            old_node = params.get(param)
            if old_node != node:
                data_dict = {'name': param[8:], 'node_id': node}
                context_ = {'model': model, 'session': model.Session,
                            'user': c.user or c.author, 'save': 'save' in request.params,
                            'for_edit': True,
                            'parent': request.params.get('parent', None),
                            'allow_partial_update': True }
                save = get_action('package_update')(context_, data_dict)
                if save:
                    count = count + 1
    h.flash_notice("%d Materials Assigned to %s" % (count, node.title()))


class OrganizationPlugin(plugins.SingletonPlugin, DefaultOrganizationForm):
    plugins.implements(plugins.IGroupForm, inherit=True)
    plugins.implements(plugins.interfaces.IOrganizationController, inherit=True)

    def before_view(self, pkg_dict):
        params = parse_params(request.params)
        node = params.pop('bulk_action.node_assign', None)
        if node:
            update_node_of_materials(node, params)
            id = pkg_dict.get('name', None)
            # Would be good if we could call the read method here so it populates
            # the c variables before rendering bulk_process.html as normal.
            # Instead we redirect to the read page which isn't the right behaviour.
            # e.g. super(OrganizationPlugin, self).read(id)
            redirect(h.url_for(controller="organization",
                     action="read", id=id))
        else:
            return pkg_dict

    def group_types(self):
        return ['organization']

    def is_fallback(self):
        return False

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


