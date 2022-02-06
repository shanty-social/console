from api.app import app
from api.views.auth import root, login, logout, authorize, WhoamiResource
from api.views.wifi import NetworkResource, scan  # noqa: E402
from api.views.settings import SettingResource  # noqa: E402
from api.views.services import ServiceResource, refresh  # noqa: E402
from api.views.tasks import TaskResource, TaskLogResource  # noqa: E402


# API endpoints.
# Set up urls and views.
# Home page (in production mode, vue application.)
app.add_url_rule('/', view_func=root)
app.add_url_rule('/api/users/login/', view_func=login)
app.add_url_rule('/api/users/logout/', view_func=logout)
app.add_url_rule('/api/users/authorize/', view_func=authorize)
app.add_url_rule('/api/users/whoami/', view_func=WhoamiResource.as_detail())
app.add_url_rule('/api/wifi/scan/', view_func=scan, methods=['POST'])
NetworkResource.add_url_rules(app, rule_prefix='/api/wifi/networks/')
SettingResource.add_url_rules(app, rule_prefix='/api/settings/')
ServiceResource.add_url_rules(app, rule_prefix='/api/services/registry/')
app.add_url_rule(
    '/api/services/refresh/', view_func=refresh, methods=['POST'])
TaskResource.add_url_rules(app, rule_prefix='/api/tasks/')
#app.add_url_rule('/api/tasks/<pk>/log/', view_func=TaskLogResource.as_list())
