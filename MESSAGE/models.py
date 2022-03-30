from django.db import models
from datetime import datetime
from DRC.core.DRCCommonUtil import KEYGEN
from PRODUCT.models import Product
import logging
from DRC.settings import PROJECT_NAME
from django.contrib.auth.models import User as AuthUser

__module_name = f'{PROJECT_NAME}.' + __name__ + '::'
logger = logging.getLogger(__module_name)


def generate_message_id():
    start = datetime.now().microsecond
    message_id = 'MSG_' + KEYGEN.getRandom_Digit(12)
    while Message.objects.filter(message_id=message_id):
        logger.warning(':: generate_generate_message_id: duplicate Message Id: {}'.format(message_id))
        message_id = 'MSG_' + KEYGEN.getRandom_StringDigit(26)
    end = datetime.now().microsecond
    logger.error('generate_generate_message_id -> ' + str(end - start) + 'ms')
    return message_id


# Create your models here.
class Message(models.Model):
    message_id = models.SlugField(max_length=16, default=generate_message_id, auto_created=True, unique=True,
                                  blank=False, null=False, primary_key=True, editable=False)
    title = models.CharField(max_length=50, blank=False, null=False)
    body = models.TextField(max_length=500, blank=False, null=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    receiver = models.ForeignKey(AuthUser, related_name='receiver', on_delete=models.CASCADE)
    read_status = models.BooleanField(default=False)
    sender = models.ForeignKey(AuthUser, related_name='sender', on_delete=models.DO_NOTHING)
