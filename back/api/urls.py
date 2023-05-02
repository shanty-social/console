from api.app import app
from api.views.oauth import OAuthClientResource
from api.views.settings import SettingResource  # noqa: E402
from api.views.tasks import TaskResource, TaskLogResource  # noqa: E402
from api.views.frontends import FrontendResource
from api.views.backends import BackendResource
from api.views.hosts import HostResource
from api.views.messages import MessageResource
from api.views.users import UserResource


HostResource.add_url_rules(app, rule_prefix='/api/hosts/')
SettingResource.add_url_rules(app, rule_prefix='/api/settings/')
TaskResource.add_url_rules(app, rule_prefix='/api/tasks/')
TaskLogResource.add_url_rules(app, rule_prefix='/api/tasks/<task_pk>/log/')
FrontendResource.add_url_rules(app, rule_prefix='/api/frontends/')
BackendResource.add_url_rules(app, rule_prefix='/api/backends/')
MessageResource.add_url_rules(app, rule_prefix='/api/messages/')
UserResource.add_url_rules(app, rule_prefix='/api/users/')
OAuthClientResource.add_url_rules(app, rule_prefix='/api/oauth/')
