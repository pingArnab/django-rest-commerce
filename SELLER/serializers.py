from .models import Seller
from rest_framework import serializers


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
