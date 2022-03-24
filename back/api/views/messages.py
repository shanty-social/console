import logging

from flask import request
from flask_peewee.utils import get_object_or_404
from restless.preparers import FieldsPreparer

from wtfpeewee.orm import model_form

from api.models import Message
from api.views import BaseResource, Form, abort


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


MessageForm = model_form(Message, base_class=Form)

message_preparer = FieldsPreparer(fields={
    'subject': 'subject',
    'body': 'body',
    'read': 'read',
})


class MessageResource(BaseResource):
    "Manage messages."
    preparer = message_preparer

    def list(self):
        "List all messages."
        read = request.args.get('read', '').lower() == 'true'
        messages = Message.select()
        if read:
            messages = messages.where(Message.read == read)
        return messages

    def detail(self, pk):
        "Retrieve single message."
        return get_object_or_404(Message, Message.id == pk)

    def create(self):
        "Create new domain(s)."
        form = MessageForm(self.data)
        if not form.validate():
            abort(400, form.errors)
        message = Message.create({
            'subject': form.subject.data,
            'body': form.body.data,
        })
        return message

    def delete(self, pk):
        "Delete message."
        message = get_object_or_404(Message, Message.id == pk)
        message.delete_instance()
