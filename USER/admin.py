from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from .models import UserProfile, UserAddress, Cart


# Register your models here.
class UserProfileAdmin(admin.ModelAdmin):
    def full_name(self, instance):
        try:
            return instance.user.get_full_name()
        except ObjectDoesNotExist as e:
            return 'ERROR!!\n {}'.format(e)

    def email(self, instance):
        try:
            return instance.user.email
        except ObjectDoesNotExist as e:
            return 'ERROR!!\n {}'.format(e)

    list_display = (
        'user', 'verified', 'full_name', 'email', 'ph_no', 'profile_image', 'cart',
    )
    search_fields = [
        'ph_no', 'user__username', 'user__first_name', 'user__last_name', 'user__email',
    ]
    list_filter = ('verified',)


class UserAddressAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'name', 'ph_no', 'pin', 'address_line_1',
        'landmark', 'city', 'state', 'country', 'address_type', 'address_category',
    )
    search_fields = [
        'user__username', 'user__first_name', 'user__last_name', 'user__email', 'name', 'ph_no', 'pin',
        'address_line_1', 'address_line_2',
        'landmark', 'city', 'state', 'country',
    ]
    list_filter = ('address_type', 'address_category',)


class CartAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'product', 'quantity'
    )
    search_fields = [
        'user__username', 'user__first_name', 'user__last_name', 'user__email',
        'product__product_id', 'product__product_name',
    ]
    # list_filter = ('address_type',  'address_category',)


admin.site.register(UserAddress, UserAddressAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Cart, CartAdmin)
