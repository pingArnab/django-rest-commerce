import datetime
import logging

from django.db.models import Sum, F
from django.http import Http404
from .models import Order, Transaction
from USER.models import UserAddress, UserProfile
from django.utils import timezone
from DRC.settings import PROJECT_NAME

__module_name = f'{PROJECT_NAME}.' + __name__ + '::'
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
            Order.STATUS.RETURNED,
            Order.STATUS.CANCELED,
        ]
    order = Order.objects.filter(
        order_status__in=order_status,
        product__seller__user_id=seller.id
    ).order_by(shorting_string)
    return order


def get_seller_order_stat(seller):
    new_orders = Order.objects.filter(
        product__seller__user_id=seller.id,
        order_status__in=[Order.STATUS.PLACED, Order.STATUS.READY_FOR_SHIPPING]
    )
    total_new_order = new_orders.count()
    total_pending_order = new_orders.filter(order_status=Order.STATUS.PLACED).count()
    new_order_stat = {
        'total': total_new_order,
        'new': total_pending_order,
        'progress': int(((total_new_order - total_pending_order) / total_new_order) * 100) if total_new_order else None
    }

    total_ordered_count = Order.objects.filter(
        product__seller__user_id=seller.id,
        order_status__in=[Order.STATUS.PLACED, Order.STATUS.READY_FOR_SHIPPING,
                          Order.STATUS.DISPATCHED, Order.STATUS.OUT_FOR_DELIVERY, Order.STATUS.DELIVERED]
    ).count()
    undelivered_ordered_count = Order.objects.filter(
        product__seller__user_id=seller.id,
        order_status__in=[Order.STATUS.DISPATCHED, Order.STATUS.OUT_FOR_DELIVERY]
    ).count()
    all_order_stat = {
        'total': total_ordered_count or 0,
        'undelivered': undelivered_ordered_count or 0,
        'progress': int(((total_ordered_count - undelivered_ordered_count) / total_ordered_count) * 100) if total_ordered_count else None
    }
    return new_order_stat, all_order_stat


def get_seller_customer_stat(seller):
    total_customer_count = Order.objects.filter(
        product__seller__user_id=seller.id
    ).values('buyer').distinct().count()
    new_customer_count = Order.objects.filter(
        product__seller__user_id=seller.id,
        created_at__lte=datetime.datetime.now().astimezone() - datetime.timedelta(days=7)
    ).values('buyer').distinct().count()
    return {
        'total': total_customer_count or 0,
        'new': new_customer_count or 0,
        'progress': int((new_customer_count / total_customer_count) * 100) if total_customer_count else None
    }


def get_seller_sales_stat(seller):
    monthly_total_sale = Order.objects.filter(
        product__seller__user_id=seller.id,
        placed_at__month=datetime.date.today().month,
        placed_at__year=datetime.date.today().year,
        order_status__in=Order.POSITIVE_ORDER_STATUS
    ).values('product__seller').annotate(total_sale=Sum(F('actual_price') - F('discount')))
    today_total_sale = Order.objects.filter(
        product__seller__user_id=seller.id,
        placed_at__day=datetime.date.today().day,
        placed_at__month=datetime.date.today().month,
        placed_at__year=datetime.date.today().year,
        order_status__in=Order.POSITIVE_ORDER_STATUS
    ).values('product__seller').annotate(total_sale=Sum(F('actual_price') - F('discount')))
    tomorrow_total_sale = Order.objects.filter(
        product__seller__user_id=seller.id,
        placed_at__day=datetime.date.today().day - 1,
        placed_at__month=datetime.date.today().month,
        placed_at__year=datetime.date.today().year,
        order_status__in=Order.POSITIVE_ORDER_STATUS
    ).values('product__seller').annotate(total_sale=Sum(F('actual_price') - F('discount')))

    monthly = monthly_total_sale[0].get('total_sale') if monthly_total_sale else 0
    today = today_total_sale[0].get('total_sale') if today_total_sale else 0
    tomorrow = tomorrow_total_sale[0].get('total_sale') if tomorrow_total_sale else 0
    # 'progress': int(((tomorrow_total_sale - today_total_sale) / tomorrow_total_sale) * 100)
    # print(monthly)
    # print(tomorrow)
    # print(today)
    # progress = [tomorrow-today, today-tomorrow]
    return {
        'monthly': monthly,
        'today': today,
        'tomorrow': tomorrow,
        'progress':  int(((tomorrow - today) / tomorrow) * 100) if tomorrow else None
    }


def getUserOrdersDict(user, filters=None):
    order = Order.objects.values(
        'order_id', 'seller', 'product__product_name', 'product__product_id',
        'product__primary_image', 'product_quantity', 'sold_price', 'shipping_address',
        'order_status', 'placed_at', 'last_updated_at', 'transaction', 'transaction__reference_id',
        'shipped_at', 'delivered_at', 'returned_at', 'canceled_at'
    ).filter(
        buyer__user=user,
        # order_status__in=filters
    ).order_by('-created_at')
    return order


def getTransactionOrdersDict(transaction):
    order = Order.objects.values(
        'order_id', 'buyer', 'product',
        'product_quantity', 'sold_price', 'shipping_address',
        'order_status', 'placed_at', 'last_updated_at',
        'shipped_at', 'delivered_at', 'returned_at', 'canceled_at'
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
