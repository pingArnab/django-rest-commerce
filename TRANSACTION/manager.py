import logging

from django.db import transaction
from django.http import Http404
from .models import Order, Transaction
from USER.models import UserAddress, UserProfile
from django.utils import timezone

__module_name = 'CTmela.' + __name__ + '::'
logger = logging.getLogger(__module_name)


def getSellerOrdersDict(seller, status=''):
    if status.upper() in ['NEW']:
        shorting_string = '-placed_at'
        order_status = [Order.STATUS.PLACED, Order.STATUS.READY_FOR_SHIPPING]
    elif status.upper() in ['ONGOING']:
        shorting_string = '-placed_at'
        order_status = [Order.STATUS.DISPATCHED, Order.STATUS.OUT_FOR_DELIVERY]
    elif status.upper() in ['RETURN']:
        shorting_string = '-placed_at'
        order_status = [Order.STATUS.REQUESTED_FOR_REFUND, Order.STATUS.RETURNED]

    elif status.upper() in ['PLACED', Order.STATUS.PLACED]:
        shorting_string = '-placed_at'
        order_status = [Order.STATUS.PLACED]
    elif status.upper() in ['DISPATCHED', Order.STATUS.DISPATCHED]:
        shorting_string = '-last_updated_at'
        order_status = [Order.STATUS.DISPATCHED]
    elif status.upper() in ['OUT_FOR_DELIVERY', Order.STATUS.OUT_FOR_DELIVERY]:
        shorting_string = '-last_updated_at'
        order_status = [Order.STATUS.OUT_FOR_DELIVERY]
    elif status.upper() in ['DELIVERED', Order.STATUS.DELIVERED]:
        shorting_string = '-delivered_at'
        order_status = [Order.STATUS.DELIVERED]
    elif status.upper() in ['REQUESTED_FOR_REFUND', Order.STATUS.REQUESTED_FOR_REFUND]:
        shorting_string = '-last_updated_at'
        order_status = [Order.STATUS.REQUESTED_FOR_REFUND]
    elif status.upper() in ['RETURNED', Order.STATUS.RETURNED]:
        shorting_string = '-last_updated_at'
        order_status = [Order.STATUS.RETURNED]
    else:
        if status.upper() == 'UPDATES':
            shorting_string = '-last_updated_at'
        else:
            shorting_string = '-created_at'
        order_status = [
            Order.STATUS.PLACED,
            Order.STATUS.READY_FOR_SHIPPING,
            Order.STATUS.DISPATCHED,
            Order.STATUS.OUT_FOR_DELIVERY,
            Order.STATUS.DELIVERED,
            Order.STATUS.REQUESTED_FOR_REFUND,
            Order.STATUS.RETURNED
        ]
    order = Order.objects.values(
        'order_id', 'product__product_name', 'product__product_id',
        'product__primary_image', 'product_quantity', 'transaction__shipping_address',
        'actual_price', 'discount', 'product_quantity',
        'order_status', 'placed_at', 'last_updated_at',
        'shipped_at', 'delivered_at', 'refund_at'
    ).filter(
        order_status__in=order_status
    ).order_by(shorting_string)
    return order


def getUserOrdersDict(user, filters=None):
    order = Order.objects.values(
        'order_id', 'seller', 'product__product_name', 'product__product_id',
        'product__primary_image', 'product_quantity', 'sold_price', 'transaction__shipping_address',
        'order_status', 'placed_at', 'last_updated_at', 'transaction', 'transaction__reference_id',
        'shipped_at', 'delivered_at', 'refund_at'
    ).filter(
        buyer__user=user,
        # order_status__in=filters
    ).order_by('-created_at')
    return order


def getTransactionOrdersDict(transaction):
    order = Order.objects.values(
        'order_id', 'buyer', 'product',
        'product_quantity', 'sold_price', 'transaction__shipping_address',
        'order_status', 'placed_at', 'last_updated_at',
        'shipped_at', 'delivered_at', 'refund_at'
    ).filter(
        transaction=transaction,
    ).order_by('-created_at')
    return order


def initiateOrderTransaction(buyer: UserProfile, address: UserAddress, uuid, reference_id=None):
    transaction = None
    order_list = []
    try:
        transaction = Transaction.create_transaction(
            reference_id=reference_id,
            buyer=buyer,
            products=buyer.cart,
            total_amount=buyer.calculate_cart_total_amount()['total_selling_price'],
            total_discount=buyer.calculate_cart_total_amount()['total_discount'],
            total_delivery_charge=buyer.calculate_cart_total_amount()['total_delivery_charge'],
            address=address.getAddressJson()
        )
        logger.debug(str(__name__) + '::checkout <step-3>: Transaction created: {}'.format(
            transaction) + '   ---UUID({})'.format(uuid))
        logger.debug(str(__name__) + '::checkout <step-3>: cart: {}'.format(
            buyer.get_cart_products().count()) + '   ---UUID({})'.format(uuid))
        for product in buyer.get_cart_products():
            order = Order.create_order(
                buyer=buyer,
                seller=product.seller,
                product=product,
                quantity=product.quantity,
                transaction=transaction,
                sold_price=product.get_price()['selling_price'],
                discount=product.get_price()['discount']
            )
            order_list.append(order)
            logger.debug('::checkout <step-3>:initiateOrderTransaction-> Order created: {}'.format(
                order) + '   ---UUID({})'.format(uuid))
    except Exception as ex:
        if transaction:
            transaction.delete()
        for odr in order_list:
            odr.delete()
        logger.exception('::checkout: initiateOrderTransaction->  <step-3>:' + str(ex) + '   ---UUID({})'.format(uuid))
        raise Http404('Unexpected Error Caught [{}]'.format(uuid))

    return transaction


def completeOrderTransaction(payment_method, transaction):
    transaction.payment_method = payment_method
    transaction.payment_status = Transaction.STATUS.SUCCESS
    transaction.save()
    orders = transaction.order_set.all()
    orders.update(order_status=Order.STATUS.PLACED, placed_at=timezone.now())
    logger.debug('Order placed: ' + str(orders))
    for order in orders:
        order.product.in_stock -= order.product_quantity
        order.product.save()


def makePayment(payment_option):
    if not payment_option:
        return {'status': 405, 'msg': 'Please select an payment procedure'}
    elif payment_option == Transaction.METHOD.PAY_ON_DELIVERY:
        return {
            'status': 200,
            'msg': 'Payment Successful',
            'method': Transaction.METHOD.PAY_ON_DELIVERY
        }
    else:
        return {'status': 405, 'msg': 'Only \'Pay on Delivery\' is available for your address'}
