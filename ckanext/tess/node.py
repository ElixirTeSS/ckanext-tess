import re
import os
import logging
import genshi
import cgi
import datetime
from urllib import urlencode

from pylons.i18n import get_lang

import ckan.lib.base as base
import ckan.lib.helpers as h
import ckan.lib.maintain as maintain
import ckan.lib.navl.dictization_functions as dict_fns
import ckan.logic as logic
import ckan.lib.search as search
import ckan.model as model
import ckan.new_authz as new_authz
import ckan.lib.plugins
import ckan.plugins as plugins
from ckan.common import OrderedDict, c, g, request, _

log = logging.getLogger(__name__)

render = base.render
abort = base.abort

NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError
check_access = logic.check_access
get_action = logic.get_action
tuplize_dict = logic.tuplize_dict
clean_dict = logic.clean_dict
parse_params = logic.parse_params

lookup_group_plugin = ckan.lib.plugins.lookup_group_plugin


class NodeController(base.BaseController):

    group_type = 'node'

    ## hooks for subclasses
    def _node_form(self):
        return lookup_group_plugin(group_type).group_form()

    def _form_to_db_schema(self, group_type=None):
        return lookup_group_plugin(group_type).form_to_db_schema()

    def _db_to_form_schema(self, group_type=None):
        '''This is an interface to manipulate data from the database
        into a format suitable for the form (optional)'''
        return lookup_group_plugin(group_type).db_to_form_schema()

    def _setup_template_variables(self, context, data_dict, group_type=None):
        return lookup_group_plugin(group_type).\
            setup_template_variables(context, data_dict)

    def _new_template(self, group_type):
        return lookup_group_plugin(group_type).new_template()

    def _index_template(self, group_type):
        return lookup_group_plugin(group_type).index_template()

    def _about_template(self, group_type):
        return lookup_group_plugin(group_type).about_template()

    def _read_template(self, group_type):
        return lookup_group_plugin(group_type).read_template()

    def _history_template(self, group_type):
        return lookup_group_plugin(group_type).history_template()

    def _edit_template(self, group_type):
        return lookup_group_plugin(group_type).edit_template()

    def _activity_template(self, group_type):
        return lookup_group_plugin(group_type).activity_template()

    def _admins_template(self, group_type):
        return lookup_group_plugin(group_type).admins_template()

    def _bulk_process_template(self, group_type):
        return lookup_group_plugin(group_type).bulk_process_template()

