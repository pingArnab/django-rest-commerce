from django.contrib import admin
from .models import Category, Product, Review


def save_all_selected(modeladmin, request, queryset):
    for item in queryset:
        item.save()


# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'category_id', 'category_name', 'primary_image', 'primary_image_placeholder',
        'parent', 'max_discount', 'sell_count',
    )
    search_fields = [
        'category_id', 'category_name', 'max_discount',
        'sell_count', 'parent',
    ]
    actions = [save_all_selected]


class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'product_id', 'product_name', 'price', 'offer_price', 'seller',
        'sell_count', 'rating', 'offer', 'created_at', 'last_modified',
    )
    search_fields = [
        'product_id', 'product_name', 'sub_title', 'price', 'offer_price',
        'short_description', 'long_description', 'seller__seller_id', 'rating',
    ]
    list_filter = ('rating', 'offer')
    readonly_fields = ['primary_image_placeholder', ]
    actions = [save_all_selected]


class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'product', 'title', 'rating',
    )
    search_fields = [
        'user__username', 'user__email',
        'user__first_name', 'user__last_name',
        'user__userprofile_ph_no', 'product__product_id', 'product__product_name',
        'price', 'title', 'rating',
    ]
    actions = [save_all_selected]


admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Review, ReviewAdmin)
