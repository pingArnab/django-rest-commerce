from django.db.migrations import serializer

from .models import Cart
from rest_framework import serializers
from .models import UserAddress
from django.contrib.auth.models import User as AuthUser


class UserProfileSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    ph_no = serializers.SerializerMethodField()
    is_verified = serializers.SerializerMethodField()

    class Meta:
        model = AuthUser
        fields = (
            'username', 'name', 'email', 'image', 'ph_no', 'is_verified'
        )

    @staticmethod
    def get_name(user: AuthUser):
        return {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'full_name': user.get_full_name()
        }

    @staticmethod
    def get_image(user: AuthUser):
        image = None
        if user.userprofile.profile_image.url != '/media/image/USER/Default-user.png':
            image = user.userprofile.profile_image.url
        return image

    @staticmethod
    def get_ph_no(user: AuthUser):
        return user.userprofile.ph_no

    @staticmethod
    def get_is_verified(user: AuthUser):
        return user.userprofile.verified


class UserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddress
        fields = (
            'id', 'name', 'ph_no', 'pin', 'address_line_1', 'address_line_2',
            'landmark', 'city', 'state', 'country', 'address_type',
            'address_category',
        )


class CartSerializer(serializers.ModelSerializer):
    product_id = serializers.CharField(source='product.product_id', read_only=True)
    product_name = serializers.CharField(source='product.product_name', read_only=True)
    primary_image = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = (
            'product_id',  'product_name',  'primary_image', 'price', 'quantity'
        )

    @staticmethod
    def get_price(cart: Cart):
        return cart.product.get_price().get('selling_price')

    @staticmethod
    def get_primary_image(cart: Cart):
        return cart.product.primary_image.url
