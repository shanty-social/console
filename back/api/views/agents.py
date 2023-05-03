import logging

from flask import request
from flask_peewee.utils import get_object_or_404

from restless.preparers import FieldsPreparer

from wtfpeewee.orm import model_form

from api.views import BaseResource, Form, abort
from api.models import Agent


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


AgentForm = model_form(Agent, base_class=Form)


agent_preparer = FieldsPreparer(fields={
    'id': 'id',
    'uuid': 'uuid',
    'name': 'name',
    'description': 'description',
    'token': 'token',
    'activated': 'activated',
    'created': 'created',
})


class AgentResource(BaseResource):
    "Manage Agents."
    preparer = agent_preparer

    def is_authenticated(self):
        if self.endpoint == 'list' and request.method == 'POST':
            return True
        return super().is_authenticated()

    def list(self):
        "List agents."
        uuid = request.args.get('uuid')
        name = request.args.get('name')
        token = request.args.get('token')
        activated = request.args.get('activated')
        agents = Agent.select()
        if uuid:
            uuid = agents.where(Agent.uuid == uuid)
        if name:
            agents = agents.where(Agent.name == name)
        if token:
            agents = agents.where(Agent.token == token)
        if activated:
            agents = agents.where(Agent.activated == activated)
        return agents

    def detail(self, pk):
        "Retrieve single agent."
        return get_object_or_404(Agent, Agent.id == pk)

    def create(self):
        "Create new agent(s)."
        form = AgentForm(self.data)
        if not form.validate():
            abort(400, form.errors)
        agent, created = Agent.get_or_create(
            uuid=form.uuid.data, defaults={
                'name': form.name.data,
                'description': form.description.data,
                'token': form.token.data,
                'activated': False,
            }
        )
        if not created:
            form.populate_obj(agent)
            agent.save()
        return agent

    def update(self, pk):
        "Update single agent."
        agent = get_object_or_404(Agent, Agent.id == pk)
        form = AgentForm(self.data, obj=agent)
        if not form.validate():
            abort(400, form.errors)
        form.populate_obj(agent)
        agent.save()
        return agent

    def delete(self, pk):
        "Delete single agent."
        agent = get_object_or_404(Agent, Agent.id == pk)
        agent.delete_instance()
