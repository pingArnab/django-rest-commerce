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

    class Meta:
        model = Transaction
        fields = (
            'reference_id', 'orders',
            'billing_address', 'shipping_address', 'payment_method'
        )

    @staticmethod
    def get_billing_address(transaction: Transaction):
        return transaction.get_billing_address()

    @staticmethod
    def get_shipping_address(transaction: Transaction):
        return transaction.get_shipping_address()

    @staticmethod
    def get_orders(transaction: Transaction):
        return OrderShortSerializer(transaction.order_set.all(), many=True).data
