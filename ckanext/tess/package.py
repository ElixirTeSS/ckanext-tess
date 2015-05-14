import ckan.plugins.toolkit as toolkit
import ckan.plugins as plugins

class PackagePlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IDatasetForm, inherit=True)


    def _modify_package_schema(self, schema):
        #Add training_material_url custom field
        schema.update({
            'training_material_url': [toolkit.get_validator('ignore_missing'), toolkit.get_validator('url_validator'), toolkit.get_converter('convert_to_extras')]
        })
        return schema

    def create_package_schema(self):
        # grab the default schema
        schema = super(PackagePlugin, self).create_package_schema()
        schema = self._modify_package_schema(schema)
        return schema

    def update_package_schema(self):
        # grab the default schema
        schema = super(PackagePlugin, self).update_package_schema()
        schema = self._modify_package_schema(schema)
        return schema


    def show_package_schema(self):
        schema = super(PackagePlugin, self).show_package_schema()
        schema.update({
            'training_material_url': [toolkit.get_converter('convert_from_extras'), toolkit.get_validator('check_missing')]
        })
        return schema

    def is_fallback(self):
        return False


    def package_types(self):
        # This plugin doesn't handle any special package types
        return []