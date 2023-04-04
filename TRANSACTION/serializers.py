from rest_framework import serializers
from .models import Order, Transaction


class OrderSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    billing_address = serializers.SerializerMethodField()
    shipping_address = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
            'order_id', 'order_status', 'product', 'track_update',
            'created_at', 'delivered_at', 'returned_at', 'canceled_at',
            'billing_address', 'shipping_address', 'price'
        )

    @staticmethod
    def get_billing_address(order: Order):
        return order.get_billing_address()

    @staticmethod
    def get_shipping_address(order: Order):
        return order.get_shipping_address()

    @staticmethod
    def get_price(order: Order):
        return {
            "subtotal": order.actual_price * order.product_quantity,  # Sum of actual prices
            "total_shipping": order.total_delivery_charge,  # Sum of shipping
            "total": order.total_price + order.total_price_delivery,  # subtotal + total_shipping
            "discount": order.discount * order.product_quantity,  # sum of discounts
            "grand_total": order.total_price_delivery  # total - discount
        }

    @staticmethod
    def get_product(order: Order):
        return {
            'product_id': order.product.product_id,
            'product_name': order.product.product_name,
            'primary_image': {
                'url': order.product.primary_image.url,
                'placeholder': order.product.primary_image_placeholder
            },
            'quantity': order.product_quantity,
            'sold_price': order.price
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
        return order.price

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
        return transaction.get_price()
