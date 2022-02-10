from api.app import app
from api.views import root
from api.views.auth import (
    oauth_start, oauth_authorize, oauth_end, WhoamiResource, login, logout,
)
from api.views.settings import SettingResource  # noqa: E402
from api.views.tasks import TaskResource, TaskLogResource  # noqa: E402
from api.views.domains import DomainResource
from api.views.endpoints import (
    HostResource, EndpointResource, open_port, check_port,
)


# API endpoints.
# Set up urls and views.
# Home page (in production mode, vue application.)
app.add_url_rule('/', view_func=root)
app.add_url_rule(
    '/api/oauth/<string:service_name>/', methods=['GET'],
    view_func=oauth_start)
app.add_url_rule(
    '/api/oauth/<string:service_name>/end/', methods=['GET'],
    view_func=oauth_end)
app.add_url_rule(
    '/api/oauth/<string:service_name>/authorize/', methods=['GET'],
    view_func=oauth_authorize)
app.add_url_rule('/api/users/login/', methods=['POST'], view_func=login)
app.add_url_rule('/api/users/logout/', methods=['POST'], view_func=logout)
app.add_url_rule('/api/users/whoami/', view_func=WhoamiResource.as_detail())
app.add_url_rule('/api/ports/open/', methods=['POST'], view_func=open_port)
app.add_url_rule('/api/ports/check/', methods=['POST'], view_func=check_port)
HostResource.add_url_rules(app, rule_prefix='/api/hosts/')
SettingResource.add_url_rules(app, rule_prefix='/api/settings/')
TaskResource.add_url_rules(app, rule_prefix='/api/tasks/')
DomainResource.add_url_rules(app, rule_prefix='/api/domains/')
EndpointResource.add_url_rules(app, rule_prefix='/api/endpoints/')
TaskLogResource.add_url_rules(app, rule_prefix='/api/tasks/<task_pk>/log/')
