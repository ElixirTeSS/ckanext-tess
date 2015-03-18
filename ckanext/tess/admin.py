
import ckan.plugins.toolkit as toolkit
import ckan.plugins as plugins
from pylons import c
import ckan.lib.helpers as h
import os
import operator
from ckan.controllers.home import HomeController
from ckan.common import OrderedDict, c, g, request, _
import ckan.lib.base as base
import ckan.logic as logic
import ckan.model as model
import ckan.new_authz as new_authz
get_action = logic.get_action
parse_params = logic.parse_params
redirect = base.redirect

from ckan.lib.plugins import DefaultGroupForm


def get_all_material_names_and_ids():
    c.admin = new_authz.is_sysadmin(c.user)
    if c.admin: #get every single training material
        try:
            materials = toolkit.get_action("package_search")\
                (data_dict={'rows': 5000, 'sort': 'name asc'})
            return materials.get('results')
        except:
            return []
    else: # get just the materials you've added if not admin
        context = {'for_edit': True,
              'auth_user_obj': c.userobj,
              'session': model.Session,
              'user': c.user or c.author, 'model': model}

        data_dict = {'id': c.user, 'include_datasets': True}
        try:
            materials = get_action('user_show')(context, data_dict)
            return materials.get('datasets')
        except:
            return []


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



class AdminController(HomeController):

    def bulk_process_materials(self):
        c.materials = get_all_material_names_and_ids()
        if c.materials:
            return base.render('node/bulk_process_materials.html')
        else:
            h.flash_error('Whoops! You do not have any training materials to attribute to a node. Try adding some')
            redirect(h.url_for(controller='user', action='read', id=c.user))

    def save_process(self):
        datum = parse_params(request.params)
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author,
                   'save': 'save' in request.params,
                   'for_edit': True,
                   'parent': request.params.get('parent', None)
        }
        count = 0
        for data in datum:
            try:
                data_dict = {'id': data, 'node_id': datum.get(data)}
                context['allow_partial_update'] = True
                save = get_action('package_update')(context, data_dict)
                if save:
                    count = count+1
            except:
                print 'error'
        h.flash_notice('%d Training Materials updated' % count)
        base.redirect(h.url_for(controller='ckanext.tess.admin:AdminController',
                                action='bulk_process_materials'))
