from django.contrib import admin
from .models import Transaction, Order


# Register your models here.
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        'reference_id', 'payable_amount',
        'payment_method', 'payment_info', 'payment_status', 'shipping_address',
    )

    search_fields = [
        'reference_id', 'seller__user__username', 'seller__user__first_name',
        'total_amount', 'shipping_address',
    ]


class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_id', 'product', 'product_quantity', 'created_at',
        'placed_at', 'order_status', 'refund_transaction',
    )

    search_fields = [
        'order_id', 'buyer__user__username', 'buyer__user__first_name',
        'product__product_id', 'product__product_name',
        'order_status', 'refund_transaction__reference_id', 'transaction__reference_id',
    ]


admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Order, OrderAdmin)
