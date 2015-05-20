import ckan.plugins.toolkit as toolkit
import ckan.plugins as plugins

class PackagePlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IDatasetForm, inherit=True)


    def create_package_schema(self):
        print "create_package_schema\n"
        # grab the default schema
        schema = super(PackagePlugin, self).create_package_schema()
        schema = self._modify_dataset_schema(schema)
        return schema


    def update_package_schema(self):
        print "update_package_schema\n"
        # grab the default schema
        schema = super(PackagePlugin, self).update_package_schema()
        schema = self._modify_dataset_schema(schema)
        return schema


    def show_package_schema(self):
        print "show_package_schema\n"
        # Import core converters and validators
        _convert_from_extras = toolkit.get_converter('convert_from_extras')
        _not_missing = toolkit.get_validator('not_missing')
        _not_empty = toolkit.get_validator('not_empty')
        _url_validator = toolkit.get_validator('url_validator')

        schema = super(PackagePlugin, self).show_package_schema()

        schema.update({
            'training_material_url': [_not_missing, _not_empty, _url_validator, _convert_from_extras]
        })
        return schema


    def _modify_dataset_schema(schema):
        print "_modify_dataset_schema\n"
         #Import core converters and validators
        _convert_to_extras = toolkit.get_converter('convert_to_extras')
        _not_missing = toolkit.get_validator('not_missing')
        _not_empty = toolkit.get_validator('not_empty')
        _url_validator = toolkit.get_validator('url_validator')

        schema.update({
            'training_material_url': [_not_missing, _not_empty, _url_validator, _convert_to_extras]
        })
        return schema


    def is_fallback(self):
        return False


    def package_types(self):
        # This plugin doesn't handle any special package/dataset types
        return []