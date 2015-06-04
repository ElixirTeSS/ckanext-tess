import logging

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit


from ckanext.tess.model.tables import setup as model_setup
from ckanext.tess.model.tables import TessMaterialNode, TessMaterialEvent, TessEvents, TessGroup, TessDomainObject, TessDataset

log = logging.getLogger(__name__)


class TessrelationsPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IMapper)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'tessrelations')
        log.debug("Running update method.")
        model_setup()

    #def configure(self, config):
    #    log.debug("Running configure method.")
    #    model_setup()

    #def update_config(self, config):


    def before_insert(self, mapper, connection, instance):
        log.info("TR INSERTING: %r", instance)

    def after_insert(self, mapper, connection, instance):
        log.info("TR INSERTED: %r", instance)

    def before_delete(self, mapper, connection, instance):
        log.info("TR DELETING: %r", instance)
        if isinstance(instance, Group):
            log.info("GROUP DELETING: %r", instance)
            # Instead, see if the group field is set

    def after_delete(self, mapper, connection, instance):
        log.info("TR DELETED: %r", instance)

    def before_update(self, mapper, connection, instance):
        pass

    def after_update(self, mapper, connection, instance):
        pass
