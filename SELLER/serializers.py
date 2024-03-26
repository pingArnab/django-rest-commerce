import datetime

import PRODUCT.models
from .models import Seller
from rest_framework import serializers
from PRODUCT.models import Product


class SellerSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    is_verified = serializers.SerializerMethodField()

    class Meta:
        model = Seller
        fields = (
            'seller_id', 'name', 'image', 'ph_no', 'alt_ph_no', 'profile_image',
            'address', 'gstin', 'total_sale', 'is_verified'
        )

    @staticmethod
    def get_name(seller: Seller):
        return {
            'first_name': seller.user.first_name,
            'last_name': seller.user.last_name,
            'full_name': seller.user.get_full_name()
        }

    @staticmethod
    def get_image(seller: Seller):
        image = None
        # if user.userprofile.profile_image.url != '/media/image/USER/Default-user.png':
        #     image = user.userprofile.profile_image.url
        return image

    @staticmethod
    def get_is_verified(seller: Seller):
        return seller.verified


class ProductSerializer(serializers.ModelSerializer):
    selling_price = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'product_id', 'product_name', 'primary_image',
            'in_stock', 'selling_price', 'sell_count', 'category'
        )

    def get_selling_price(self, product: Product):
        datetime_now = datetime.datetime.now().astimezone()
        if product.offer:
            if product.offer_start < datetime_now < product.offer_end:
                return product.offer_price
        return product.price

    def get_category(self, product: Product):
        return product.category.values('category_id', 'category_name')
