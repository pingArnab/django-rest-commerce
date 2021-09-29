import USER.models
from rest_framework import serializers
from PRODUCT.models import Product, Category, Review
from USER.models import UserProfile
from django.contrib.auth.models import User as AuthUser


class ProductListSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()
    is_wishlisted = serializers.SerializerMethodField()
    primary_image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'product_id', 'product_name', 'primary_image',
            'price', 'in_stock', 'rating', 'is_wishlisted'
        )

    @staticmethod
    def get_price(product):
        return product.get_price()

    def get_is_wishlisted(self, product):
        user: AuthUser = self.context.get('user')
        if user and UserProfile.objects.filter(user__username=user.username):
            if user.userprofile.wishlist.filter(product_id=product.product_id):
                return True
        return False

    @staticmethod
    def get_primary_image(category):
        return {
            'url': category.primary_image.url,
            'placeholder': category.primary_image_placeholder
        }


class ProductSearchSuggestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            'product_id', 'product_name',
        )


class SingleProductSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()
    primary_image = serializers.SerializerMethodField()
    is_wishlisted = serializers.SerializerMethodField()
    cod_applicable = serializers.SerializerMethodField()
    other_images = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    categories = serializers.SerializerMethodField()
    seller = serializers.SerializerMethodField()
    short_description = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'product_id', 'product_name', 'primary_image',
            'other_images', 'price', 'in_stock', 'rating',
            'is_wishlisted', 'max_per_cart', 'tags', 'seller',
            'short_description', 'long_description', 'rating',
            'categories', 'warranty', 'cod_applicable'
        )

    @staticmethod
    def get_price(product):
        return product.get_price()

    @staticmethod
    def get_primary_image(product):
        return {
            'url': product.primary_image.url,
            'placeholder': product.primary_image_placeholder
        }

    @staticmethod
    def get_cod_applicable(product):
        return bool(product.cod)

    def get_is_wishlisted(self, product):
        user: AuthUser = self.context.get('user')
        if user and UserProfile.objects.filter(user__username=user.username):
            if user.userprofile.wishlist.filter(product_id=product.product_id):
                return True
        return False

    @staticmethod
    def get_other_images(product):
        image_list = list()
        product.optional_image_1 and image_list.append(product.optional_image_1.url)
        product.optional_image_2 and image_list.append(product.optional_image_2.url)
        product.optional_image_3 and image_list.append(product.optional_image_3.url)
        return image_list

    @staticmethod
    def get_tags(product):
        return str(product.tag).splitlines()

    @staticmethod
    def get_categories(product):
        categories_list = list()
        categories_qs = product.category.all()
        for category in categories_qs:
            categories_list.append({
                'id': category.category_id,
                'name': category.category_name,
            })
        return categories_list

    @staticmethod
    def get_seller(product):
        seller = product.seller
        return {
            'id': seller.seller_id,
            'name': seller.user.get_full_name(),
            'image': seller.profile_image.url if seller.profile_image else None
        }

    @staticmethod
    def get_short_description(product):
        return product.short_description.splitlines()


class CategoryListSerializer(serializers.ModelSerializer):
    sub_categories = serializers.SerializerMethodField()
    primary_image = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = (
            'category_id', 'category_name', 'primary_image',
            'sub_categories'
        )

    @staticmethod
    def get_primary_image(category):
        return {
            'url': category.primary_image.url,
            'placeholder': category.primary_image_placeholder
        }

    @staticmethod
    def get_sub_categories(category):
        sub_categories_list = category.category_set.all()
        if sub_categories_list:
            return CategoryListSerializer(sub_categories_list, many=True).data
        else:
            return None


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = (
            'author', 'title', 'description', 'rating',
            'timestamp'
        )

    @staticmethod
    def get_author(review: Review):
        return {
            'name': review.user.get_full_name(),
            'username': review.user.username,
            'image': review.user.userprofile.profile_image.url
        }
