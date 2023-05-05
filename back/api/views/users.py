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
    'is_active': 'is_active',
    'is_admin': 'is_admin',
    'is_agent': 'is_agent',
})


class UserResource(BaseResource):
    "Manage Users."
    preparer = user_preparer
    extra_actions = {
        'login': ['POST'],
        'logout': ['POST'],
        'whoami': ['GET'],
        'activated': ['GET'],
    }

    def is_authenticated(self):
        if self.endpoint in ('login', 'whoami', 'activated'):
            return True
        elif self.endpoint == 'list' and request.method == 'POST':
            # NOTE: create()
            return True
        return super().is_authenticated()

    def list(self):
        return User.select()

    def detail(self, pk):
        return get_object_or_404(User, User.username == pk)

    def create(self):
        form = UserForm(self.data)
        if not form.validate():
            abort(400, form.errors)
        user, created = User.get_or_create(
            username=form.username.data, defaults={'name': form.name.data})
        user.set_password(form.password.data)
        # NOTE: Anonymously created users are initially inactive.
        user.is_active = form.is_active.data if super().is_authenticated() \
                                             else False  # noqa: E127
        user.save()
        return user

    def update(self, pk):
        user = get_object_or_404(User, User.id == pk)
        form = UserForm(self.data, obj=user)
        if not form.validate():
            abort(400, form.errors)
        if form.name.data:
            user.name = form.name.data
        if form.password.data:
            user.set_password(form.password.data)
        user.save()
        return user

    def delete(self, pk):
        user = get_object_or_404(User, User.username == pk)
        user.delete_instance()

    def login(self):
        form = LoginForm(request.get_json())
        if not form.validate():
            abort(400, form.errors)

        return log_in_user(form.username.data, form.password.data)

    @skip_prepare
    def logout(self):
        log_out_user()

    def whoami(self):
        "Details of logged in user."
        user = get_logged_in_user()
        if not user:
            abort(401)
        return user

    @skip_prepare
    def activated(self):
        return User.select().exists()
