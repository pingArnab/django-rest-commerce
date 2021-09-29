from django.contrib import admin
from .models import Carousel, SubHeading, OTP


# Register your models here.
class CarouselAdmin(admin.ModelAdmin):
    list_display = (
        'seq_no', 'name', 'url', 'image', 'image_placeholder',
    )
    search_fields = [
        'seq_no', 'name', 'url', 'image',
    ]


# Register your models here.
class SubHeadingAdmin(admin.ModelAdmin):
    list_display = (
        'seq_no', 'name', 'url', 'image', 'image_placeholder',
    )
    search_fields = [
        'seq_no', 'name', 'url', 'image',
    ]


# Register your models here.
class OTPAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'otp_valid_upto',
    )
    search_fields = [
        'user',
    ]


admin.site.register(Carousel, CarouselAdmin)
admin.site.register(SubHeading, SubHeadingAdmin)
admin.site.register(OTP, OTPAdmin)
