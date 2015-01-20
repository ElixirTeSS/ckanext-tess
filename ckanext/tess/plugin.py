'''plugin.py

'''
import ckan.plugins.toolkit as toolkit
import os
from ckan.plugins import implements, SingletonPlugin
from ckan.plugins import IConfigurer
from ckan.plugins import IRoutes

class TeSSPlugin(SingletonPlugin):
    '''TeSS CKAN plugin.

    '''
    # Declare that this class implements IConfigurer.
    #plugins.implements(plugins.IConfigurer)
    implements(IConfigurer, inherit=True)
    implements(IRoutes, inherit=True)

    def update_config(self, config):

        # Add this plugin's templates dir to CKAN's extra_template_paths, so
        # that CKAN will use this plugin's custom templates.
        # 'templates' is the path to the templates dir, relative to this
        # plugin.py file.
        #toolkit.add_template_directory(config, 'templates')
	#toolkit.add_public_directory(config, 'public')

	#here = os.path.dirname(__file__)
	#config['ckan.site_logo'] = 'images/TeSSLogo.png'

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


