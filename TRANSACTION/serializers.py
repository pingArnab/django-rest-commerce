from rest_framework import serializers
from .models import Order, Transaction


class OrderSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    billing_address = serializers.SerializerMethodField()
    shipping_address = serializers.SerializerMethodField()
    sold_price = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
            'order_id', 'sold_price', 'discount', 'order_status',
            'product', 'delivery_charge',
            'track_update', 'created_at', 'delivered_at', 'returned_at',
            'canceled_at', 'billing_address', 'shipping_address'
        )

    @staticmethod
    def get_billing_address(order: Order):
        return order.get_billing_address()

    @staticmethod
    def get_shipping_address(order: Order):
        return order.get_shipping_address()

    @staticmethod
    def get_sold_price(order: Order):
        return order.get_final_price()

    @staticmethod
    def get_product(order: Order):
        return {
            'product_id': order.product.product_id,
            'product_name': order.product.product_name,
            'primary_image': {
                'url': order.product.primary_image.url,
                'placeholder': order.product.primary_image_placeholder
            },
            'quantity': order.product_quantity
        }


class OrderShortSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    sold_price = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
            'order_id', 'sold_price', 'product'
        )

    @staticmethod
    def get_sold_price(order: Order):
        return order.get_final_price()

    @staticmethod
    def get_product(order: Order):
        return {
            'product_id': order.product.product_id,
            'product_name': order.product.product_name,
            'primary_image': {
                'url': order.product.primary_image.url,
                'placeholder': order.product.primary_image_placeholder
            },
            'quantity': order.product_quantity
        }


class TransactionSerializer(serializers.ModelSerializer):
    orders = serializers.SerializerMethodField()
    billing_address = serializers.SerializerMethodField()
    shipping_address = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = (
            'reference_id', 'orders',
            'billing_address', 'shipping_address',
            'price', 'payment_method'
        )

    @staticmethod
    def get_billing_address(transaction: Transaction):
        return transaction.order_set.first().get_billing_address()

    @staticmethod
    def get_shipping_address(transaction: Transaction):
        return transaction.order_set.first().get_shipping_address()

    @staticmethod
    def get_orders(transaction: Transaction):
        return OrderShortSerializer(transaction.order_set.all(), many=True).data

    @staticmethod
    def get_price(transaction: Transaction):
        subtotal = 0  # Sum of order actual_price
        total_shipping = 0  # Sum of order delivery_charge
        discount = 0  # Sum of order discount
        total = 0  # Sum of order price
        grand_total = 0  # Sum of order price
        for order in transaction.order_set.all():
            subtotal += order.actual_price
            total_shipping += order.delivery_charge
            discount += order.discount
            total += order.price
            grand_total += order.price_delivery
        return {
            'subtotal': subtotal,
            'total_shipping': total_shipping,
            'discount': discount,
            'total': total,
            'grand_total': grand_total
        }
