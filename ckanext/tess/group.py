
import ckan.plugins as plugins
from pylons import c
import ckan.model as model
import ckan.logic as logic
NotFound = logic.NotFound
get_action = logic.get_action


class GroupPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.interfaces.IGroupController, inherit=True)

    def before_view(self, group):
        if c.controller == 'group':
            group['owner'] = group_owner(group)
        return group

def group_owner(group):
    context = {'model': model, 'session': model.Session,
                'user': c.user or c.author,
                'for_view': True}
    admin = logic.get_action('member_list')(context, {'id': group.get('name'), 'object_type': 'user', 'capacity': 'admin'})
    if isinstance(admin, list) and admin[0][0]:
        user = logic.get_action('user_show')(context, {'id': admin[0][0]})
        return {'name': user.get('display_name'), 'link': user.get('id')}
    else:
        return {'name': 'unknown', 'link': '--'}


