import datetime
import logging
import traceback

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from DRC.core.exceptions import ErrorResponse
from DRC.core.DRCConstant import ErrorCode, ErrorMessage
from DRC.core.permissions import UserOnly
from django.contrib.auth.models import User as AuthUser

from DRC.settings import PROJECT_NAME
from TRANSACTION.models import Transaction
from USER.models import Cart, UserAddress
from .models import Order
from .serializers import OrderSerializer, TransactionSerializer


__module_name = f'{PROJECT_NAME}.' + __name__ + '::'
logger = logging.getLogger(__module_name)


@api_view(['GET'])
@permission_classes([IsAuthenticated, UserOnly])
def all_orders(request):
    user: AuthUser = request.user
    orders_non_pending = Order.objects.filter(
        transaction__buyer=user,
    ).exclude(
        order_status=Order.STATUS.PENDING_FOR_PAYMENT
    )
    orders_pending_for_payment = Order.objects.filter(
        transaction__buyer=user,
        order_status=Order.STATUS.PENDING_FOR_PAYMENT,
        created_at__gte=datetime.datetime.now().astimezone() - datetime.timedelta(minutes=15)
    )
    orders = orders_non_pending | orders_pending_for_payment
    return Response(OrderSerializer(orders.order_by('-created_at'), many=True).data)


# Order.objects.filter(order_status=Order) #.filter(order_status__)

@api_view(['GET'])
@permission_classes([IsAuthenticated, UserOnly])
def order_by_id(request, order_id: str):
    user: AuthUser = request.user
    if not Order.objects.filter(transaction__buyer_id=user.id, order_id=order_id):
        return ErrorResponse(code=ErrorCode.INVALID_ORDER_ID, msg=ErrorMessage.INVALID_ORDER_ID).response
    order = Order.objects.get(transaction__buyer_id=user.id, order_id=order_id)
    if (order.order_status == Order.STATUS.PENDING_FOR_PAYMENT and
            order.created_at <= datetime.datetime.now().astimezone() - datetime.timedelta(minutes=15)):
        return ErrorResponse(code=ErrorCode.Expired_ORDER, msg=ErrorMessage.Expired_ORDER).response
    return Response(OrderSerializer(order, many=False).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated, UserOnly])
def checkout_pre_process(request):
    FUNCTION_NAME = 'checkout_pre_process'
    user: AuthUser = request.user

    new_transaction = None
    new_order_list = []

    if UserAddress.objects.filter(user_id=user.id, id=request.data.get('shipping_address_id', None)):
        shipping_address: UserAddress = UserAddress.objects.get(user_id=user.id,
                                                                id=request.data.get('shipping_address_id', None))
    else:
        return ErrorResponse(code=400, msg='Shipping address missing').response

    if UserAddress.objects.filter(user_id=user.id, id=request.data.get('billing_address_id', None)):
        billing_address: UserAddress = UserAddress.objects.get(user_id=user.id,
                                                               id=request.data.get('billing_address_id', None))
    else:
        return ErrorResponse(code=400, msg='Billing address missing').response

    if not user.cart_set.all():
        return ErrorResponse(code=ErrorCode.EMPTY_CART, msg=ErrorMessage.EMPTY_CART).response

    out_of_stock_products = []
    for cart in user.cart_set.all():
        if (cart.product.in_stock - cart.quantity) < 0:
            out_of_stock_products.append(cart.product.product_id)

    if out_of_stock_products:
        logger.warning(f'{FUNCTION_NAME} -> Following products are out of stock: {out_of_stock_products.__str__()}')
        return ErrorResponse(
            code=400,
            msg='Products are out of stock',
            extra={
                "out_of_stock_products": out_of_stock_products
            }
        ).response

    payment_method = request.data.get('payment_method')
    if not payment_method:
        return ErrorResponse(code=ErrorCode.PAYMENT_METHODE_MISSING, msg=ErrorMessage.PAYMENT_METHODE_MISSING).response
    elif not (payment_method in [Transaction.METHOD.PAY_ON_DELIVERY]):
        return ErrorResponse(code=400, msg='Only pay on delivery available').response

    try:
        total_price = Cart.total_amount_by_username(username=user.username)
        total_discount = Cart.total_discount_by_username(username=user.username)
        total_delivery_charge = Cart.total_deliver_charge_by_username(username=user.username)

        Cart.total_discount_by_username(username=user.username)
        new_transaction = Transaction.objects.create(
            amount=total_price-total_discount+total_delivery_charge,
            shipping_address=shipping_address.getAddressJson(),
            billing_address=billing_address.getAddressJson(),
            payment_method=payment_method
        )
        new_transaction.save()

        for cart in user.cart_set.all():
            new_order = Order.objects.create(
                transaction_id=new_transaction.reference_id,
                buyer=cart.user,
                product_id=cart.product.product_id,
                product_quantity=cart.quantity,
                actual_price=cart.product.get_price().get('actual_price'),
                discount=cart.product.get_price().get('discount'),
                delivery_charge=cart.product.delivery_charge,
            )
            new_order.save()
            new_order_list.append(new_order.order_id)
            user.cart_set.all().delete()
    except Exception as ex:
        if new_transaction:
            new_transaction.delete()
        for order in new_order_list:
            order.delete()
        traceback.print_exc()
        return ErrorResponse(code=400, msg='Error in checkout pre-process', details=ex.__str__()).response

    return Response({
        'transaction_id': new_transaction.reference_id,
        'orders_list': new_order_list
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, UserOnly])
def transaction_by_id(request, transaction_id: str):
    user: AuthUser = request.user
    if not Transaction.objects.filter(reference_id=transaction_id):
        return ErrorResponse(code=ErrorCode.INVALID_TRANSACTION_ID, msg=ErrorMessage.INVALID_TRANSACTION_ID).response
    transaction = Transaction.objects.get(reference_id=transaction_id)
    return Response(TransactionSerializer(transaction, many=False).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated, UserOnly])
def checkout_confirmation(request):
    FUNCTION_NAME = 'checkout_confirmation'
    user: AuthUser = request.user
    transaction_id = request.data.get('transaction_id').strip() if request.data.get('transaction_id') else None
    if not Transaction.objects.filter(reference_id=transaction_id):
        return ErrorResponse(code=ErrorCode.INVALID_TRANSACTION_ID, msg=ErrorMessage.INVALID_TRANSACTION_ID).response

    transaction = Transaction.objects.get(reference_id=transaction_id)
    if transaction.payment_status == Transaction.STATUS.SUCCESS:
        return ErrorResponse(code=ErrorCode.INVALID_TRANSACTION_ID, msg=ErrorMessage.INVALID_TRANSACTION_ID).response

    if transaction.payment_method in [Transaction.METHOD.PAY_ON_DELIVERY]:
        transaction.payment_status = Transaction.STATUS.SUCCESS
        transaction.success_at = datetime.datetime.now().astimezone()
        transaction.order_set.update(order_status=Order.STATUS.PLACED)

        out_of_stock_products = []
        for order in transaction.order_set.all():
            if (order.product.in_stock - order.product_quantity) < 0:
                out_of_stock_products.append(order.product.product_id)

        if out_of_stock_products:
            logger.warning(f'{FUNCTION_NAME} -> Following products are out of stock: {out_of_stock_products.__str__()}')
            return ErrorResponse(
                code=400,
                msg='Products are out of stock',
                extra={
                    "out_of_stock_products": out_of_stock_products
                }
            ).response

        for order in transaction.order_set.all():
            order.order_status = Order.STATUS.PLACED
            order.product.in_stock -= order.product_quantity
            order.product.sell_count += order.product_quantity
            order.product.seller.total_sale += order.product_quantity
            order.product.seller.save()
            order.placed_at = datetime.datetime.now().astimezone()
            order.product.save()
            order.save()
        transaction.save()
    else:
        return ErrorResponse(code=400, msg='Invalid payment methode').response
    return Response(TransactionSerializer(transaction, many=False).data)
