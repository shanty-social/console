from restless.preparers import FieldsPreparer
from restless.resources import skip_prepare

from flask import request
from flask_peewee.utils import get_object_or_404

import wtforms
from wtforms.validators import InputRequired
from wtfpeewee.orm import model_form

from api.views import Form
from api.auth import get_logged_in_user, log_in_user, log_out_user
from api.views import BaseResource, abort
from api.models import User


UserForm = model_form(User, base_class=Form)


class LoginForm(Form):
    username = wtforms.StringField('Username', [InputRequired()])
    password = wtforms.StringField('Password', [InputRequired()])


user_preparer = FieldsPreparer(fields={
    'username': 'username',
    'name': 'name',
    'active': 'active',
})


class UserResource(BaseResource):
    "Manage Users."
    preparer = user_preparer

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.http_methods.update({
            'login': {
                'POST': 'login',
            },
            'logout': {
                'POST': 'logout',
            },
            'whoami': {
                'GET': 'whoami',
            },
        })

    @classmethod
    def add_url_rules(cls, app, rule_prefix, endpoint_prefix=None):
        super().add_url_rules(
            app, rule_prefix, endpoint_prefix=endpoint_prefix)
        app.add_url_rule(
            rule_prefix + 'login/',
            endpoint=cls.build_endpoint_name('login', endpoint_prefix),
            view_func=cls.as_view('login'),
            methods=['POST']
        )
        app.add_url_rule(
            rule_prefix + 'logout/',
            endpoint=cls.build_endpoint_name('logout', endpoint_prefix),
            view_func=cls.as_view('logout'),
            methods=['POST']
        )
        app.add_url_rule(
            rule_prefix + 'whoami/',
            endpoint=cls.build_endpoint_name('whoami', endpoint_prefix),
            view_func=cls.as_view('whoami'),
            methods=['GET']
        )

    def is_authenticated(self):
        if self.endpoint == 'login':
            return True
        return super().is_authenticated()

    def list(self):
        return User.select()

    def detail(self, pk):
        return User.get(User.username == pk)

    def create(self):
        form = UserForm.from_json(self.data)
        if not form.validate():
            abort(400, form.errors)
        user, created = User.get_or_create(
            username=form.username.data, defaults={'name': form.name.data})
        user.set_password(form.password.data)
        user.save()
        return user

    def delete(self, pk):
        user = get_object_or_404(User, User.username == pk)
        user.delete_instance()

    @skip_prepare
    def logout(self):
        log_out_user()

    def whoami(self):
        "Details of a particular service."
        return get_logged_in_user()

    def login(self):
        form = LoginForm(request.get_json())
        if not form.validate():
            abort(400, form.errors)

        return log_in_user(form.username.data, form.password.data)
