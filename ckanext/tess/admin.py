
import ckan.plugins.toolkit as toolkit
import ckan.plugins as plugins
from pylons import c
import ckan.lib.helpers as h
import os
import operator

from ckan.lib.plugins import DefaultGroupForm


def get_all_material_names_and_ids():
    mats = toolkit.get_action("package_search")\
        (data_dict={'rows':5000, 'sort':'alphabet asc', 'facet.field':['name', 'description']})
    return mats.get('results')


class AdminPlugin(plugins.SingletonPlugin, DefaultGroupForm):
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.ITemplateHelpers, inherit=True)
    plugins.implements(plugins.interfaces.IMapper, inherit=True)

    def get_helpers(self):
        return {
            'get_all_material_names_and_ids': get_all_material_names_and_ids
        }

    def before_map(self, map):
        map.connect('bulk-process', '/admin/nodes', controller='ckanext.tess.admin:AdminController', action='bulk_process_materials')
        map.connect('bulk-process-save', '/admin/nodes/save', controller='ckanext.tess.admin:AdminController', action='save_process')
        return map

from ckan.controllers.home import HomeController
from ckan.common import OrderedDict, c, g, request, _
import ckan.lib.base as base
import ckan.logic as logic
import ckan.model as model
get_action = logic.get_action
parse_params = logic.parse_params

class AdminController(HomeController):

    def bulk_process_materials(self):
        return base.render('node/bulk_process_materials.html')

    def save_process(self):
        datum = parse_params(request.params)
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author,
                   'save': 'save' in request.params,
                   'for_edit': True,
                   'parent': request.params.get('parent', None)
        }
        for data in datum:
            try:
                data_dict = {'id': data, 'node_id': datum.get(data)}
                context['allow_partial_update'] = True
                print context
                print data_dict
                save = get_action('package_update')(context, data_dict)
            except:
                print 'error'

        base.redirect(h.url_for(controller='ckanext.tess.admin:AdminController',
                                action='bulk_process_materials'))
