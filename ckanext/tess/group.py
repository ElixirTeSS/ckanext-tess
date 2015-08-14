
import ckan.plugins as plugins
import ckan.model as model
import ckan.logic as logic
import ckan.plugins.toolkit as toolkit
import ckan.lib.plugins as plugs
from pylons import c
NotFound = logic.NotFound
get_action = logic.get_action

class GroupPlugin(plugins.SingletonPlugin, plugs.DefaultGroupForm):

    plugins.implements(plugins.IGroupForm, inherit=False)
    plugins.implements(plugins.interfaces.IGroupController, inherit=True)

    def before_view(self, group):
        if c.controller == 'group':
            group['owner'] = group_owner(group)
            if c.userobj and c.userobj.id:
                print group['owner'].get('link') == c.userobj.id
                print group
                group['display'] = True
            else:
                group['display'] = False

        return group


    def group_types(self):
        return ['group']

    def is_fallback(self):
        return True

    def form_to_db_schema(self):
        schema = super(GroupPlugin, self).form_to_db_schema()
        schema = self._modify_group_schema(schema)
        return schema

    def db_to_form_schema(self):
        schema = super(GroupPlugin, self).form_to_db_schema()
        _convert_from_extras = toolkit.get_converter('convert_from_extras')
        _ignore_missing = toolkit.get_validator('ignore_missing')
        _boolean = toolkit.get_validator('boolean_validator')
        default_validators = [_convert_from_extras, _ignore_missing, _boolean]
        schema.update({
            'private': default_validators
        })

        return schema

    def _modify_group_schema(self, schema):
         #Import core converters and validators
        _convert_to_extras = toolkit.get_converter('convert_to_extras')
        _ignore_missing = toolkit.get_validator('ignore_missing')
        _boolean = toolkit.get_validator('boolean_validator')

        default_validators = [_ignore_missing, _boolean, _convert_to_extras]
        schema.update({
            'private': default_validators
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

