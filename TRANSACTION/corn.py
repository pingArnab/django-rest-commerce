from .models import Transaction
import logging
from DRC.settings import PROJECT_NAME

__module_name = f'{PROJECT_NAME}.' + __name__ + '::'
logger = logging.getLogger(__module_name)


def print_all_transaction_ids():
    FUNCTION_NAME = 'print_all_transaction_ids_corn'
    logger.warning(f'{FUNCTION_NAME}-> (Corn job) Transaction Count: {Transaction.objects.all().count()}')
