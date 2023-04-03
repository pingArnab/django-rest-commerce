import logging
from datetime import datetime
from threading import *
import blurhash
from django.utils import timezone
from django.db import models
from SELLER.models import Seller
from DRC.core.exceptions import ErrorResponse
from DRC.core.DRCCommonUtil import KEYGEN
from DRC.core.DRCConstant import Constant
from DRC.core.DRCConstant import ErrorCode, ErrorMessage
from django.contrib.auth.models import User as AuthUser
from django.core.validators import MaxValueValidator, MinValueValidator
from DRC.settings import PROJECT_NAME

__module_name = f'{PROJECT_NAME}.' + __name__ + '::'
logger = logging.getLogger(__module_name)


def format_price(raw_price):
    if '.' not in raw_price.__str__():
        return raw_price.__str__()
    price = str(round(raw_price, 2)).split('.')
    price[1] = ('' if price[1] == '0' else '.' + price[1])
    price[1] = (price[1] + '0' if len(price[1]) == 2 else price[1])
    return price[0] + price[1]


# Create your models here.
def generate_category_id():
    start = datetime.now().microsecond
    category_id = 'CAT_' + KEYGEN.getRandom_Digit(12)
    while Category.objects.filter(category_id=category_id):
        logger.error(':: generateCategoryId: duplicate Category Id: {}'.format(category_id))
        category_id = 'CAT_' + KEYGEN.getRandom_StringDigit(12)
    end = datetime.now().microsecond
    logger.error('generateCategoryId -> ' + str(end - start) + 'micros')
    return category_id


def generate_product_id():
    start = datetime.now().microsecond
    product_id = 'PRO_' + KEYGEN.getRandom_Digit(12)
    while Product.objects.filter(product_id=product_id):
        logger.error(':: generateProductId: duplicate Product Id: {}'.format(product_id))
        product_id = 'PRO_' + KEYGEN.getRandom_StringDigit(26)
    end = datetime.now().microsecond
    logger.error('generateProductId -> ' + str(end - start) + 'ms')
    return product_id


class Category(models.Model):

    # image Upload Path Customizer
    def generate_file_path(self, filename=None):
        return '___uploads/{folder_name}/{sub_folder_name}/{file_name}.{file_extension}'.format(
            folder_name=self.__class__.__name__,
            sub_folder_name=self.category_id,
            file_name=KEYGEN.getRandom_StringDigit(20),
            file_extension=str(filename).split('.')[-1]
        )

    category_id = models.SlugField(max_length=16, default=generate_category_id, auto_created=True, unique=True,
                                   blank=False, null=False, primary_key=True, editable=False)
    category_name = models.CharField(max_length=150, blank=False, null=False)
    primary_image = models.ImageField(upload_to=generate_file_path)
    primary_image_placeholder = models.CharField(max_length=50, null=True, blank=True, editable=False)
    sell_count = models.IntegerField(default=0)

    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

    def get_primary_image_thumbnail(self):
        return blurhash.encode(self.primary_image, x_components=4, y_components=3)

    def save(self, *args, **kwargs):
        self.primary_image_placeholder = self.get_primary_image_thumbnail()
        super(Category, self).save(*args, **kwargs)

    def max_discount(self):
        max_dis = 0
        for i in self.product_set.all():
            # print(i, max_dis < i.get_price()[2])
            max_dis = i.get_price()['discount_percentage'] if max_dis < i.get_price()[
                'discount_percentage'] else max_dis
        return max_dis

    def __str__(self):
        return '{}'.format(self.category_name)


class Product(models.Model):

    # image Upload Path Customizer
    def generate_file_path(self, filename=None):
        return '___uploads/{folder_name}/{sub_folder_name}/{file_name}.{file_extension}'.format(
            folder_name=self.__class__.__name__,
            sub_folder_name=self.product_id,
            file_name=KEYGEN.getRandom_StringDigit(20),
            file_extension=str(filename).split('.')[-1]
        )

    # product details
    product_id = models.SlugField(max_length=16, default=generate_product_id, auto_created=True, unique=True,
                                  blank=False,
                                  null=False, primary_key=True, editable=False)
    product_name = models.CharField(max_length=250, blank=False, null=False)
    price = models.FloatField(default=0.0)
    short_description = models.TextField(max_length=1000, null=True, blank=True)
    long_description = models.TextField(null=True, blank=True)

    # images
    primary_image = models.ImageField(upload_to=generate_file_path)
    primary_image_placeholder = models.CharField(max_length=50, null=True, blank=True)
    optional_image_1 = models.ImageField(upload_to=generate_file_path, null=True, blank=True)
    optional_image_2 = models.ImageField(upload_to=generate_file_path, null=True, blank=True)
    optional_image_3 = models.ImageField(upload_to=generate_file_path, null=True, blank=True)

    # Group
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    category = models.ManyToManyField(Category)

    # Sells
    sell_count = models.IntegerField(default=0, editable=False)
    in_stock = models.IntegerField(default=1)
    rating = models.FloatField(default=0, editable=False)
    rating_count = models.IntegerField(default=0, editable=False)
    max_per_cart = models.IntegerField(default=5)

    # offer
    offer = models.BooleanField(default=False)
    offer_start = models.DateTimeField(null=True, blank=True)
    offer_price = models.FloatField(default=1)
    offer_end = models.DateTimeField(null=True, blank=True)

    # Extras
    features = models.TextField(default="{}")
    tag = models.TextField(max_length=500, blank=True, null=True)
    warranty = models.FloatField(null=True, blank=True)
    cod = models.BooleanField(null=True, blank=True)

    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    # delivery
    delivery_charge = models.FloatField(default=0.0)
    delivery_charge_per_product = models.BooleanField(default=False)

    def get_primary_image_thumbnail(self):
        return blurhash.encode(self.primary_image, x_components=4, y_components=3)

    def update_primary_image_thumbnail(self):
        self.primary_image_placeholder = blurhash.encode(self.primary_image, x_components=4, y_components=3)
        self.save()

    def get_primary_image_url(self):
        return '/media/{}'.format(self.primary_image)

    def get_price(self):
        # price_list = [format_price(self.price), 0.0, 0, 0.0]
        price_obj = {
            'delivery_charge': self.delivery_charge,
            'selling_price': self.price,
            'actual_price': self.price,
            'discount_percentage': 0,
            'discount': 0.0
        }
        time_now = timezone.now()
        if not self.offer:
            return price_obj
        if self.offer_start is None or self.offer_end is None:
            return price_obj
        if self.offer_start <= time_now <= self.offer_end:
            price_obj['selling_price'] = self.offer_price  # Selling Price
            price_obj['actual_price'] = self.price  # Actual Price
            price_obj['discount_percentage'] = round(
                ((self.price - self.offer_price) / self.price) * 100)  # Discount Percentage
            price_obj['discount'] = self.price - self.offer_price  # Discount
        return price_obj

    def get_text_price(self):
        price_obj = self.get_price()
        price_text_obj = {
            'selling_price': format_price(price_obj.get('selling_price')),  # Selling Price
            'actual_price': format_price(price_obj.get('actual_price')),  # Actual Price
            'discount_percentage': format_price(price_obj.get('discount_percentage')),  # Discount Percentage
            'discount': format_price(price_obj.get('discount')),  # Discount
            'delivery_charge': format_price(price_obj.get('delivery_charge'))  # Discount
        }
        return price_text_obj

    def get_rating_star(self):
        color_list = ["none"] * 5
        color_list[0: round(self.rating)] = ["#2ecaa0"] * round(self.rating)
        svg = Constant.STAR_SVG.format(id=1, color=color_list)
        return svg

    def get_short_description(self):
        short_description_list = self.short_description.split('\r\n')
        list_text = self.short_description.strip().replace('\r', '').split('\n')
        ulli = '<ul>{}</ul>'
        li = ''
        for i in list_text:
            li += """
                    <li>{}</li>
                """.format(i)
        return ulli.format(li)

    def set_warranty(self, years=0, months=0, days=0):
        if months:
            days += months * 30
        if years:
            days += years * 365
        self.warranty = days

    def get_warranty_text(self):
        if not self.warranty:
            return None
        text = ''
        number_of_days = int(self.warranty)
        years = number_of_days // 365
        months = (number_of_days - years * 365) // 30
        days = (number_of_days - years * 365 - months * 30)

        if years:
            text += f'{years}Years '
        if months:
            text += f'{months}Months '
        if days:
            text += f'{days}Days '
        return text

    def __str__(self):
        return f'{self.product_id} [{self.product_name[:15]}]'

    ##########################
    # API
    def addable_quantity_checker(self, quantity):
        if quantity < 1:
            return None, ErrorResponse(
                code=ErrorCode.MIN_NO_OF_PRODUCT_PER_CART_EXCEEDED,
                msg=ErrorMessage.MIN_NO_OF_PRODUCT_PER_CART_EXCEEDED
            )
        if quantity > self.max_per_cart:
            return None, ErrorResponse(
                code=ErrorCode.MAX_NO_OF_PRODUCT_PER_CART_EXCEEDED,
                msg=ErrorMessage.MAX_NO_OF_PRODUCT_PER_CART_EXCEEDED
            )
        if quantity > self.in_stock:
            return None, ErrorResponse(
                code=ErrorCode.NOT_ENOUGH_PRODUCT_IN_STOCK,
                msg=ErrorMessage.NOT_ENOUGH_PRODUCT_IN_STOCK
            )
        return quantity, None


class Review(models.Model):
    user = models.ForeignKey(AuthUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, models.CASCADE)
    title = models.CharField(max_length=150, blank=True, null=True)
    description = models.TextField(max_length=2000, null=True, blank=True)
    rating = models.FloatField(default=0.0, validators=[
        MinValueValidator(0.0), MaxValueValidator(5.0)
    ])

    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'product')
