import logging

from django.contrib.auth.models import User as AuthUser

from DRC.settings import PROJECT_NAME
from MESSAGE.models import Message

__module_name = f'{PROJECT_NAME}.' + __name__ + '::'
logger = logging.getLogger(__module_name)


def get_seller_context(user: AuthUser):
    context = {}
    unread_count = Message.objects.filter(
        receiver=user, read_status=False
    ).count()
    context['unread_message_count'] = unread_count
    return context
