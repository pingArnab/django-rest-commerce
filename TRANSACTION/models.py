import json
import logging
from django.db import models
from DRC.core.DRCCommonUtil import KEYGEN
from django.contrib.auth.models import User as AuthUser
from PRODUCT.models import Seller, Product
from USER.models import UserProfile
from DRC.settings import PROJECT_NAME

__module_name = f'{PROJECT_NAME}.' + __name__ + '::'
logger = logging.getLogger(__module_name)


def generateOrderRefId():
    order_id = 'odr_' + KEYGEN.getRandom_StringDigit(26)
    while Order.objects.filter(order_id=order_id):
        logger.error(':: generateOrderRefId: duplicate Order Id: {}'.format(order_id))
        order_id = 'odr_' + KEYGEN.getRandom_StringDigit(26)
    return order_id


def generateTransactionRefId():
    reference_id = 'tnx_' + KEYGEN.getRandom_StringDigit(26)
    while Transaction.objects.filter(reference_id=reference_id):
        logger.error(':: generateTransactionRefId: Transaction Reference Id: {}'.format(reference_id))
        reference_id = 'tnx_' + KEYGEN.getRandom_StringDigit(26)
    return reference_id


class Transaction(models.Model):
    class STATUS:
        INITIATED = 'I'
        SUCCESS = 'S'
        FAILED = 'F'
        PENDING = 'P'
        REFUND = 'R'

    class METHOD:
        CARD = 'CRD'
        PAY_ON_DELIVERY = 'POD'
        UPI = 'UPI'
        NET_BANKING = 'NET'
        WALLET = 'WLT'

    __PAYMENT_STATUS_CHOICES = [
        ('I', 'Initiated'),
        ('S', 'Success'),
        ('F', 'Failure'),
        ('P', 'Pending'),
        ('R', 'Refund'),
    ]
    __PAYMENT_METHOD_CHOICES = [
        ('CRD', 'Card'),
        ('POD', 'Pay On Delivery'),
        ('UPI', 'UPI'),
        ('WLT', 'Wallet'),
        ('NET', 'Net Banking'),
    ]

    reference_id = models.CharField(primary_key=True, max_length=30, default=generateTransactionRefId, editable=False)

    amount = models.FloatField(default=0, blank=False, null=False)

    created_at = models.DateTimeField(auto_now_add=True)
    success_at = models.DateTimeField(blank=True, null=True)
    refund_at = models.DateTimeField(blank=True, null=True)

    payment_method = models.CharField(max_length=4, choices=__PAYMENT_METHOD_CHOICES, blank=False, null=False)
    payment_info = models.TextField(max_length=200, blank=True, null=True)
    payment_gateway_ref = models.CharField(max_length=50, blank=True, null=True)
    payment_status = models.CharField(max_length=1, choices=__PAYMENT_STATUS_CHOICES, default='I')  # i/s/f/p

    @staticmethod
    def create_transaction(products, total_amount, total_discount, address, total_delivery_charge=0.0,
                           reference_id=None,
                           billing_address=None):
        billing_address = billing_address or address
        if reference_id:
            transaction = Transaction.objects.create(
                reference_id=reference_id,
                purchased_products=products,
                amount=total_amount + total_delivery_charge - total_discount,
                shipping_address=address,
                billing_address=billing_address,
            )
        else:
            transaction = Transaction.objects.create(
                purchased_products=products,
                amount=total_amount + total_delivery_charge - total_discount,
                shipping_address=address,
                billing_address=billing_address,
            )
        transaction.save()
        return transaction

    def get_price(self):
        subtotal = 0  # Sum of order actual_price
        total_shipping = 0  # Sum of order delivery_charge
        discount = 0  # Sum of order discount
        total = 0  # Sum of order price
        grand_total = 0  # Sum of order price
        for order in self.order_set.all():
            subtotal += order.actual_price * order.product_quantity
            total_shipping += order.total_delivery_charge
            discount += order.discount * order.product_quantity
            total += order.total_price
            grand_total += order.total_price_delivery
        return {
            'subtotal': subtotal,
            'total_shipping': total_shipping,
            'discount': discount,
            'total': total,
            'grand_total': grand_total
        }

    def __str__(self):
        return '{}'.format(self.reference_id)


class Order(models.Model):
    __ORDER_STATUS_CHOICES = [
        ('PFP', 'Pending for Payment'),
        ('PLC', 'Placed'),
        ('RFS', 'Ready for Shipping'),
        ('DPC', 'Dispatched'),
        ('OFD', 'Out for Delivery'),
        ('DLV', 'Delivered'),
        ('RFR', 'Requested for Return'),
        ('RTN', 'Returned'),
        ('CNL', 'Canceled'),
    ]

    class STATUS:
        PENDING_FOR_PAYMENT = 'PFP'
        PLACED = 'PLC'
        READY_FOR_SHIPPING = 'RFS'
        DISPATCHED = 'DPC'
        OUT_FOR_DELIVERY = 'OFD'
        DELIVERED = 'DLV'
        REQUESTED_FOR_REFUND = 'RFR'
        RETURNED = 'RTN'
        CANCELED = 'CNL'

    # Non-cancelable order type list
    NON_CANCELABLE_LIST = [
        STATUS.CANCELED,
        STATUS.OUT_FOR_DELIVERY,
        STATUS.DELIVERED,
        STATUS.RETURNED,
        STATUS.PENDING_FOR_PAYMENT
    ]
    POSITIVE_ORDER_STATUS = [
        STATUS.PLACED,
        STATUS.DISPATCHED,
        STATUS.OUT_FOR_DELIVERY,
        STATUS.DELIVERED,
        STATUS.REQUESTED_FOR_REFUND,
    ]
    ON_TRANSIT_ORDER_STATUS = [
        STATUS.DISPATCHED,
        STATUS.OUT_FOR_DELIVERY,
    ]

    order_id = models.CharField(primary_key=True, max_length=30, default=generateOrderRefId, editable=False)

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    buyer = models.ForeignKey(AuthUser, on_delete=models.CASCADE)
    product_quantity = models.IntegerField(default=1)

    actual_price = models.FloatField(default=0)
    discount = models.FloatField(default=0)
    price = models.FloatField(default=0, editable=False)
    delivery_charge = models.FloatField(default=0)
    total_delivery_charge = models.FloatField(default=0)
    total_price = models.FloatField(default=0, editable=False)
    total_price_delivery = models.FloatField(default=0, editable=False)

    order_status = models.CharField(max_length=4, blank=False, null=False,
                                    choices=__ORDER_STATUS_CHOICES, default='PFP')
    track_update = models.TextField(null=True, blank=True)

    shipping_address = models.TextField(default='{}')
    billing_address = models.TextField(default='{}')

    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)
    placed_at = models.DateTimeField(null=True, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    returned_at = models.DateTimeField(null=True, blank=True)
    canceled_at = models.DateTimeField(null=True, blank=True)

    refund_transaction = models.ForeignKey(Transaction, on_delete=models.SET_NULL,
                                           related_name='refund', null=True, blank=True)

    @staticmethod
    def create_order(product, sold_price, quantity, transaction, discount):
        order = Order.objects.create(
            product=product,
            product_quantity=quantity,
            transaction=transaction,
            sold_price=sold_price,
            discount=discount,
        )
        order.save()
        return order

    def save(self, *args, **kwargs):
        if self.product.delivery_charge_per_product:
            self.total_delivery_charge = self.delivery_charge * self.product_quantity
        else:
            self.total_delivery_charge = self.delivery_charge
        self.price = self.actual_price - self.discount
        self.total_price = self.price * self.product_quantity
        self.total_price_delivery = self.total_price + self.total_delivery_charge
        super(Order, self).save(*args, **kwargs)

    def get_final_price(self):
        return (self.actual_price - self.discount) * self.product_quantity

    def get_final_price_wih_shipping(self):
        return self.get_final_price() + self.total_delivery_charge

    def get_shipping_address(self):
        address = self.shipping_address
        return json.loads(address)

    def get_billing_address(self):
        address = self.billing_address
        return json.loads(address)

    def __str__(self):
        return '{}'.format(self.order_id)
