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
    'name': 'name',
    'token': 'token',
    'url': 'url',
    'container_id': 'container_id',
    'created': 'created',
})


class AgentResource(BaseResource):
    "Manage Agents."
    preparer = agent_preparer

    def list(self):
        "List agents."
        name = request.args.get('name')
        token = request.args.get('token')
        url = request.args.get('url')
        container_id = request.args.get('container_id')
        agents = Agent.select()
        if name:
            agents = agents.where(Agent.name == name)
        if token:
            agents = agents.where(Agent.token == token)
        if url:
            agents = agents.where(Agent.url == url)
        if container_id:
            agents = agents.where(Agent.container_id == container_id)
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
            name=form.name.data, defaults={
                'name': form.name.data,
                'token': form.token.data,
                'url': form.url.data,
                'container_id': form.container_id.data,
            }
        )
        if not created:
            form.populate_obj(agent)
            agent.save()
        return agent

    def update(self, pk):
        "Update single agent."
        agent = get_object_or_404(Agent, Agent.id == pk)
        form = AgentForm(self.data)
        if not form.validate():
            abort(400, form.errors)
        form.populate_obj(agent)
        agent.save()
        return agent

    def delete(self, pk):
        "Delete single agent."
        agent = get_object_or_404(Agent, Agent.id == pk)
        agent.delete_instance()
