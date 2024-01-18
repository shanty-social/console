from api.app import app
from api.views.oauth import OAuthClientResource
from api.views.settings import SettingResource  # noqa: E402
from api.views.tasks import TaskResource, TaskLogResource  # noqa: E402
from api.views.endpoints import EndpointResource
from api.views.hosts import HostResource
from api.views.messages import MessageResource
from api.views.users import UserResource
from api.views.network import NetworkResource
from api.views.containers import ServiceResource
from api.views.docker import proxy


app.add_url_rule('/api/docker/<path>', 'proxy', proxy)
HostResource.add_url_rules(app, rule_prefix='/api/hosts/')
SettingResource.add_url_rules(app, rule_prefix='/api/settings/')
TaskResource.add_url_rules(app, rule_prefix='/api/tasks/')
TaskLogResource.add_url_rules(app, rule_prefix='/api/tasks/<task_pk>/log/')
EndpointResource.add_url_rules(app, rule_prefix='/api/endpoints/')
MessageResource.add_url_rules(app, rule_prefix='/api/messages/')
UserResource.add_url_rules(app, rule_prefix='/api/users/')
OAuthClientResource.add_url_rules(app, rule_prefix='/api/oauth/')
NetworkResource.add_url_rules(app, rule_prefix='/api/net/')
ServiceResource.add_url_rules(app, rule_prefix='/api/services/')
