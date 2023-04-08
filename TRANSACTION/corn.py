import datetime

from MESSAGE.models import Message
import logging
from DRC.settings import PROJECT_NAME

__module_name = f'{PROJECT_NAME}.' + __name__ + '::'
logger = logging.getLogger(__module_name)


def print_all_transaction_ids():
    FUNCTION_NAME = 'print_all_transaction_ids_corn'
    msg = Message.objects.create(
        title=f'Corn Job Run -> {datetime.datetime.now().astimezone()}',
        body=f'Corn Job Run -> {datetime.datetime.now().astimezone()}',
        receiver_id=1,
        sender_id=1
    )
    msg.save()
    logger.warning(f'{FUNCTION_NAME}-> (Corn job) Triggered !')
