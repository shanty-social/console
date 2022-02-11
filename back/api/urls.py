from api.app import app
from api.views import root
from api.views.oauth import start, end, authorize
from api.views.users import UserResource
from api.views.settings import SettingResource  # noqa: E402
from api.views.tasks import TaskResource, TaskLogResource  # noqa: E402
from api.views.domains import DomainResource
from api.views.endpoints import EndpointResource
from api.views.hosts import HostResource
from api.views.ports import PortResource
from api.views.certs import CertResource, acme


# API endpoints.
# Set up urls and views.
# Home page (in production mode, vue application.)
app.add_url_rule('/', view_func=root)
app.add_url_rule(
    '/api/oauth/<string:service_name>/', methods=['GET'],
    view_func=start)
app.add_url_rule(
    '/api/oauth/<string:service_name>/end/', methods=['GET'],
    view_func=end)
app.add_url_rule(
    '/api/oauth/<string:service_name>/authorize/', methods=['GET'],
    view_func=authorize)
app.add_url_rule('/.well-know/acme-challenge/', methods=['GET'], view_func=acme)
HostResource.add_url_rules(app, rule_prefix='/api/hosts/')
SettingResource.add_url_rules(app, rule_prefix='/api/settings/')
TaskResource.add_url_rules(app, rule_prefix='/api/tasks/')
DomainResource.add_url_rules(app, rule_prefix='/api/domains/')
EndpointResource.add_url_rules(app, rule_prefix='/api/endpoints/')
TaskLogResource.add_url_rules(app, rule_prefix='/api/tasks/<task_pk>/log/')
UserResource.add_url_rules(app, rule_prefix='/api/users/')
PortResource.add_url_rules(app, rule_prefix='/api/ports/')
CertResource.add_url_rules(app, rule_prefix='/api/certs/')
