from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from .models import Seller


# Register your models here.
class SellerAdmin(admin.ModelAdmin):
    @staticmethod
    def full_name(instance):
        try:
            return instance.user.get_full_name()
        except ObjectDoesNotExist as e:
            return 'ERROR!!\n {}'.format(e)

    @staticmethod
    def email(instance):
        try:
            return instance.user.email
        except ObjectDoesNotExist as e:
            return 'ERROR!!\n {}'.format(e)

    list_display = (
        'user',  'seller_id',  'full_name',  'email',  'ph_no',
        'total_sale',  'profile_image',  'address',  'gstin', 'verified'
    )
    search_fields = [
         'seller_id', 'user__username', 'user__first_name', 'user__last_name',  'user__email',  'ph_no', 'address',  'gstin',
    ]


admin.site.register(Seller, SellerAdmin)
