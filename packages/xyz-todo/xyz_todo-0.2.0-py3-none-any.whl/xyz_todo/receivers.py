# -*- coding:utf-8 -*-
from django.dispatch import receiver
from . import signals, helper


@receiver(signals.to_create_todos, sender=None)
def create_todos(sender, **kwargs):
    return helper.create_todos(
        target=kwargs['target'],
        name=kwargs.get('name', ''),
        url=kwargs['url'],
        title=kwargs.get('title'),
        expiration=kwargs['expiration'],
        user_ids=kwargs['user_ids'])


@receiver(signals.to_cancel_todos, sender=None)
def cancel_todos(sender, **kwargs):
    return helper.cancel_todos(kwargs['target'], name=kwargs.get('name'))

@receiver(signals.todo_done, sender=None)
def done_todos(sender, **kwargs):
    return helper.todo_done(kwargs['target'], kwargs['user'], name=kwargs.get('name'))
