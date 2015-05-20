import ckan.plugins.toolkit as toolkit
import ckan.plugins as plugins

class DatasetPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IDatasetForm, inherit=True)


    # def _modify_package_schema(self, schema):
    #     #Add training_material_url custom field
    #     schema.update({
    #         'training_material_url': [toolkit.get_validator('ignore_missing'), toolkit.get_validator('url_validator'), toolkit.get_converter('convert_to_extras')]
    #     })
    #     return schema

    def create_package_schema(self):
        # grab the default schema
        schema = super(DatasetPlugin, self).create_package_schema()
        schema = self._modify_dataset_schema(schema)
        return schema


    def update_package_schema(self):
        # grab the default schema
        schema = super(DatasetPlugin, self).update_package_schema()
        schema = self._modify_dataset_schema(schema)
        return schema


    def show_package_schema(self):
        return db_to_form_schema(self)


    def form_to_db_schema_api_create(self):
        schema = super(DatasetPlugin, self).form_to_db_schema_api_create()
        schema = self._modify_dataset_schema(schema)
        return schema


    def form_to_db_schema_api_update(self):
        schema = super(DatasetPlugin, self).form_to_db_schema_api_update()
        schema = self._modify_dataset_schema(schema)
        return schema


    def form_to_db_schema(self):
        schema = super(DatasetPlugin, self).form_to_db_schema()
        schema = self._modify_dataset_schema(schema)
        return schema


    def _modify_dataset_schema(self, schema):
         #Import core converters and validators
        _convert_to_extras = toolkit.get_converter('convert_to_extras')
        _not_missing = toolkit.get_validator('not_missing')
        _not_empty = toolkit.get_validator('not_empty')
        _url_validator = toolkit.get_validator('url_validator')

        schema.update({
            'training_material_url': [_not_missing, _not_empty, _url_validator, _convert_to_extras]
        })
        return schema


    def db_to_form_schema(self):
        # Import core converters and validators
        _convert_from_extras = toolkit.get_converter('convert_from_extras')
        _not_missing = toolkit.get_validator('not_missing')
        _not_empty = toolkit.get_validator('not_empty')
        _url_validator = toolkit.get_validator('url_validator')

        schema = super(DatasetPlugin, self).form_to_db_schema()

        schema.update({
            'training_material_url': [_not_missing, _not_empty, _url_validator, _convert_from_extras]
        })
        return schema


    def is_fallback(self):
        return False


    def package_types(self):
        # This plugin doesn't handle any special package/dataset types
        return []