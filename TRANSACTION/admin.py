from django.contrib import admin
from .models import Transaction, Order


def save_all_selected(modeladmin, request, queryset):
    for item in queryset:
        item.save()


# Register your models here.
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        'reference_id', 'payment_method', 'amount', 'payment_info',
        'payment_status', 'created_at'
    )

    search_fields = [
        'reference_id', 'order__order_id', 'payment_info',
        'payment_status',
    ]
    list_filter = (
        'payment_status', 'created_at'
    )
    actions = [save_all_selected]


class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_id', 'product', 'product_quantity', 'price',
        'total_price', 'total_price_delivery',
        'buyer', 'created_at', 'last_updated_at', 'placed_at', 'order_status',
    )

    search_fields = [
        'order_id', 'buyer__username', 'buyer__first_name',
        'product__product_id', 'product__product_name',
        'order_status', 'refund_transaction__reference_id', 'transaction__reference_id',
    ]
    list_filter = (
        'order_status', 'created_at', 'placed_at', 'last_updated_at'
    )
    actions = [save_all_selected]


admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Order, OrderAdmin)
