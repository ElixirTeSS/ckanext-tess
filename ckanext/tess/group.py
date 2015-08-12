
import ckan.plugins as plugins
import ckan.model as model
import ckan.logic as logic
NotFound = logic.NotFound
get_action = logic.get_action
import ckan.plugins.toolkit as toolkit
from pylons import c


class GroupPlugin(plugins.SingletonPlugin, plugins.toolkit.DefaultGroupForm):

    plugins.implements(plugins.IGroupForm, inherit=False)

    def group_types(self):
        return ['group']

    def is_fallback(self):
        return True

    def form_to_db_schema(self):
        schema = super(GroupPlugin, self).form_to_db_schema()
        schema = self._modify_group_schema(schema)
        return schema

    def _modify_group_schema(self, schema):
         #Import core converters and validators
        _convert_to_extras = toolkit.get_converter('convert_to_extras')
        _ignore_missing = toolkit.get_validator('ignore_missing')

        default_validators = [_ignore_missing, _convert_to_extras]
        schema.update({
            'member_status': [_convert_to_extras], #true or false
            'country_code': [_convert_to_extras],
            'home_page': default_validators,
            'institutions': default_validators, # string in JSON format
            'trc': default_validators,
            'trc_email': default_validators,
            'trc_image': default_validators,
            'staff': default_validators, # in JSON format
            'carousel_image_1': default_validators,
            'carousel_image_2': default_validators,
            'carousel_image_3': default_validators,
            'twitter': default_validators
        })
        return schema




def group_owner(group):
    context = {'model': model, 'session': model.Session,
                'user': c.user or c.author,
                'for_view': True}
    admin = logic.get_action('member_list')(context, {'id': group.get('name'), 'object_type': 'user', 'capacity': 'admin'})
    if admin and isinstance(admin, list) and admin[0][0]:
        user = logic.get_action('user_show')(context, {'id': admin[0][0]})
        return {'name': user.get('display_name'), 'link': user.get('id')}
    else:
        return {'name': 'unknown', 'link': '--'}