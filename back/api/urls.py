from api.app import app
from api.views.auth import (
    root, oauth_start, oauth_authorize, oauth_end, WhoamiResource, login,
    logout
)
from api.views.settings import SettingResource  # noqa: E402
from api.views.tasks import TaskResource, TaskLogResource  # noqa: E402
from api.views.domains import DomainResource
from api.views.endpoints import EndpointResource


# API endpoints.
# Set up urls and views.
# Home page (in production mode, vue application.)
app.add_url_rule('/', view_func=root)
app.add_url_rule('/api/oauth/<string:service_name>/', view_func=oauth_start)
app.add_url_rule('/api/oauth/<string:service_name>/end/', view_func=oauth_end)
app.add_url_rule(
    '/api/oauth/<string:service_name>/authorize/', view_func=oauth_authorize)
app.add_url_rule('/api/users/login/', methods=['POST'], view_func=login)
app.add_url_rule('/api/users/logout/', methods=['POST'], view_func=logout)
app.add_url_rule('/api/users/whoami/', view_func=WhoamiResource.as_detail())
SettingResource.add_url_rules(app, rule_prefix='/api/settings/')
TaskResource.add_url_rules(app, rule_prefix='/api/tasks/')
DomainResource.add_url_rules(app, rule_prefix='/api/domains/')
EndpointResource.add_url_rules(app, rule_prefix='/api/endpoints/')
#app.add_url_rule('/api/tasks/<pk>/log/', view_func=TaskLogResource.as_list())
