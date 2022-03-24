from api.app import app
from api.views.oauth import start, end, authorize, providers, whoami
from api.views.settings import SettingResource  # noqa: E402
from api.views.tasks import TaskResource, TaskLogResource  # noqa: E402
from api.views.domains import DomainResource
from api.views.endpoints import EndpointResource
from api.views.hosts import HostResource
from api.views.ports import PortResource
from api.views.messages import MessageResource


# API endpoints.
# Set up urls and views.
# Home page (in production mode, vue application.)
app.add_url_rule('/api/whoami/', methods=['GET'], view_func=whoami)
app.add_url_rule(
    '/api/oauth/', methods=['GET'], view_func=providers)
app.add_url_rule(
    '/api/oauth/<string:service_name>/', methods=['GET'],
    view_func=start)
app.add_url_rule(
    '/api/oauth/<string:service_name>/end/', methods=['GET'],
    view_func=end)
app.add_url_rule(
    '/api/oauth/<string:service_name>/authorize/', methods=['GET'],
    view_func=authorize)
HostResource.add_url_rules(app, rule_prefix='/api/hosts/')
SettingResource.add_url_rules(app, rule_prefix='/api/settings/')
TaskResource.add_url_rules(app, rule_prefix='/api/tasks/')
DomainResource.add_url_rules(app, rule_prefix='/api/domains/')
EndpointResource.add_url_rules(app, rule_prefix='/api/endpoints/')
TaskLogResource.add_url_rules(app, rule_prefix='/api/tasks/<task_pk>/log/')
PortResource.add_url_rules(app, rule_prefix='/api/ports/')
MessageResource.add_url_rules(app, rule_prefix='/api/messages/')
