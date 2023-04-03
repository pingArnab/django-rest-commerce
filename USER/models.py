import json
import logging
import datetime

from django.db.models import Sum

from PRODUCT.models import Product
from django.db import models
from django.contrib.auth.models import User as authUser
from PRODUCT.models import Product
from DRC.core.DRCCommonUtil import KEYGEN
from DRC.settings import PROJECT_NAME

__module_name = f'{PROJECT_NAME}.' + __name__ + '::'
logger = logging.getLogger(__module_name)


# Create your models here.
class UserProfile(models.Model):
    # image Upload Path Customizer
    def uploadPathCustomizer(self, filename=None):
        return '___uploads/{folder_name}/{sub_folder_name}/{file_name}.{file_extension}'.format(
            folder_name=self.__class__.__name__,
            sub_folder_name=self.user.username,
            file_name=KEYGEN.getRandom_StringDigit(20),
            file_extension=str(filename).split('.')[-1]
        )

    # dateTime = models.DateTimeField(auto_now_add=True)
    user = models.OneToOneField(authUser, on_delete=models.CASCADE)
    ph_no = models.CharField(max_length=20, blank=False, null=False)
    profile_image = models.ImageField(upload_to=uploadPathCustomizer, default='image/USER/Default-user.png')
    cart = models.TextField(default='{}', editable=False)
    wishlist = models.ManyToManyField(Product, blank=True)

    verified = models.BooleanField(default=False)
    verification_key = models.CharField(null=True, blank=True, max_length=50, editable=False)
    key_valid_upto = models.DateTimeField(null=True, blank=True, editable=False)

    # API Start
    def get_verification_key(self):
        if not self.verified:
            key = KEYGEN.getUUID()
            self.verification_key = key
            self.save()
            return self.verification_key

    def get_reset_password_key(self):
        if not self.verified:
            key = KEYGEN.getUUID()
            self.verification_key = key
            self.key_valid_upto = datetime.datetime.now().astimezone() + datetime.timedelta(hours=1)
            self.save()
            return key

    def validate_reset_password_key(self, key: str):
        if not self.verified:
            if self.verification_key == key.strip() and self.key_valid_upto <= datetime.datetime.now().astimezone():
                self.verification_key = None
                self.save()
                return True
        return False

    def validate_verification_key(self, key: str):
        if self.verified:
            return False
        if self.verification_key == key.strip():
            self.verified = True
            self.verification_key = None
            self.save()
            return True
        return False

    # API Ends

    def get_profile_image_url(self):
        return '/media/{}'.format(self.profile_image)

    # Cart Operations
    def get_cart(self):
        try:
            cart_dict = json.loads(self.cart)
            for product_id in cart_dict:
                if not Product.objects.filter(product_id=product_id):
                    del cart_dict[product_id]
                    self.remove_from_cart(product_id=product_id)
            return cart_dict
        except Exception as ex:
            logger.error('::get_cart: Invalid cart data: {} (reset Done)'.format(self.cart) + str(ex))
            self.clean_cart()
            return {}

    def get_cart_products(self):
        products = Product.objects.none()
        for product_id, count in self.get_cart().items():
            try:
                product = Product.objects.extra(select={'quantity': "{}".format(count)}).filter(product_id=product_id)
                products = products.union(product)
            except Exception as ex:
                logger.exception("{exception}<Product id = {product_id}>".format(product_id=product_id, exception=ex))
        return products

    def get_cart_view_product_details(self):
        product_list = list()
        for product_id, count in self.get_cart().items():
            try:
                product = Product.objects.get(product_id=product_id)
                product_dict = dict()
                product_dict['product_id'] = product.product_id
                product_dict['product_name'] = product.product_name
                product_dict['selling_price'] = product.get_price()['selling_price']
                product_dict['primary_image'] = product.get_primary_image_url()
                product_dict['quantity'] = count
                product_dict['in_stock'] = product.in_stock
                product_list.append(product_dict)
            except Exception as ex:
                logger.exception("{exception}<Product id = {product_id}>".format(product_id=product_id, exception=ex))

        return product_list

    def check_if_all_product_in_stock(self):
        for product_id, count in self.get_cart().items():
            try:
                product = Product.objects.get(product_id=product_id)
                if product.in_stock < 1:
                    return False
            except Exception as ex:
                logger.exception("{exception}<Product id = {product_id}>".format(product_id=product_id, exception=ex))
        return True

    def calculate_cart_total_amount(self):
        total_actual_price = 0.0001
        total_selling_price = 0.0001
        total_discount = 0.0001
        total_delivery_charge = 0.0001
        for product_id, count in self.get_cart().items():
            logger.debug('calculate_cart_total_amount => product in cart [{}, {}]'.format(product_id, count))
            product = Product.objects.get(product_id=product_id)
            # logger.debug(product)
            total_selling_price += float(product.get_price()['selling_price']) * count
            total_actual_price += float(product.get_price()['actual_price']) * count
            total_discount += float(product.get_price()['discount']) * count
            total_delivery_charge += float(product.get_price()['delivery_charge'])

        total = {
            'total_actual_price': total_actual_price,
            'total_selling_price': total_selling_price,
            'total_discount': total_discount,
            'total_delivery_charge': total_delivery_charge,
            'discount_percentage': ((total_actual_price - total_selling_price) / total_actual_price) * 100
        }
        return total

    def add_to_cart(self, product_id: str, count: int = 1):
        cart_dict = dict(json.loads(self.cart))
        if not (type(count) is int and count > 0):
            return {'status': 400, 'msg': "Invalid Product Count <Should be a positive integer>"}
        if not (type(product_id) is str and Product.objects.filter(product_id=product_id)):
            return {'status': 400, 'msg': "Invalid Product <Product Id is invalid>"}

        product = Product.objects.get(product_id=product_id)
        if ((cart_dict.get(product_id) or 0) + count) > product.max_per_cart:
            return {
                'status': 400,
                'msg': f'Only {product.max_per_cart} of this product is available for purchase at once'
            }

        if count > product.in_stock:
            return {'status': 400, 'msg': f'Sorry, only {product.in_stock} of this product is in stock'}
        if ((cart_dict.get(product_id) or 0) + count) > product.in_stock:
            return {'status': 400, 'msg': 'Max available quantity of this product already in cart'}

        if cart_dict.get(product_id):
            cart_dict[product_id] += count
        else:
            cart_dict[product_id] = count
        self.cart = json.dumps(cart_dict)
        self.save()
        return {'status': 200, 'msg': 'Product added to cart'}

    def remove_from_cart(self, product_id: str):
        cart_dict = dict(json.loads(self.cart))
        if type(product_id) is not str:
            raise ValueError("Invalid Product <Product Id is invalid>")
        if not cart_dict.get(product_id):
            raise ValueError("Invalid Product <Product Not in cart>")
        del cart_dict[product_id]
        self.cart = json.dumps(cart_dict)
        self.save()

    def clean_cart(self):
        self.cart = '{}'
        self.save()

    def set_cart(self, cart):
        if type(cart) is dict and cart != {}:
            self.cart = json.dumps(cart)
            self.save()
        elif type(cart) is str and cart != '' and cart != '{}':
            try:
                json.load(cart)
                self.cart = cart
                self.save()
            except Exception as ex:
                raise ValueError("Invalid Cart Data <Should be a Dict or JSON>", ex)
        else:
            raise ValueError("Invalid Cart Data <Should be a Dict or JSON>")

    # Default return
    def __str__(self):
        return '{}'.format(self.user.username)


class UserAddress(models.Model):
    user = models.ForeignKey(authUser, on_delete=models.CASCADE)

    name = models.CharField(max_length=50, blank=False, null=False)
    ph_no = models.CharField(max_length=20, blank=False, null=False)
    pin = models.CharField(max_length=6, blank=False, null=False)
    address_line_1 = models.CharField(max_length=60, blank=False, null=False)
    address_line_2 = models.CharField(max_length=60, blank=True, null=True)
    landmark = models.CharField(max_length=60, blank=True, null=True)
    city = models.CharField(max_length=40, blank=True, null=True)
    state = models.CharField(max_length=40, blank=True, null=True)
    country = models.CharField(max_length=40, blank=True, null=True, default="India")
    address_type = models.CharField(max_length=40, blank=True, null=True)

    address_category = models.CharField(max_length=40, blank=True, null=True)

    last_used = models.DateTimeField(auto_now=True)

    def getAddress(self):
        address = "{name}\n{address_line_1}\n{address_line_2}\n{city}, {state} {pin}"
        return address.format(name=self.name, address_line_1=self.address_line_1,
                              address_line_2=self.address_line_2, city=self.city,
                              state=self.state, pin=self.pin
                              )

    def getJustAddress(self):
        address = "{address_line_1}\n{address_line_2}\n{city}, {state} {pin}"
        return address.format(address_line_1=self.address_line_1,
                              address_line_2=self.address_line_2, city=self.city,
                              state=self.state, pin=self.pin
                              )

    def getAddressJson(self):
        address = {
            'name': self.name,
            'address_line_1': self.address_line_1,
            'address_line_2': self.address_line_2,
            'city': self.city,
            'state': self.state,
            'pin': self.pin,
            'ph_no': self.ph_no,
            'address_type': self.address_type,
        }
        return json.dumps(address)

    def get_address_line(self):
        return "{address_line_1}, {address_line_2}".format(
            address_line_1=self.address_line_1,
            address_line_2=self.address_line_2,
        )

    def __str__(self):
        return '{}'.format(self.name)


class Cart(models.Model):
    user = models.ForeignKey(authUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    class Meta:
        unique_together = ('user', 'product')

    def get_total_price(self):
        return self.quantity * self.product.get_price().get('selling_price', 0)

    def get_total_discount(self):
        return self.quantity * self.product.get_price().get('discount', 0)

    @staticmethod
    def total_product_by_username(username: str):
        return Cart.objects.filter(user__username=username).aggregate(
            product_count=models.Sum('quantity')
        ).get('product_count') or 0

    @staticmethod
    def total_price_by_username(username: str):
        cart_list = Cart.objects.filter(user__username=username)

        total_delivery_charge = 0
        total_selling_price = 0
        total_actual_price = 0
        total_discount = 0
        for cart in cart_list:
            price_obj = cart.product.get_price()
            print(f'total_price_by_username -> {username} | {cart.product} || {price_obj} | {cart.quantity}')
            total_delivery_charge = price_obj.get('delivery_charge', 0) * cart.quantity
            if cart.product.delivery_charge_per_product:
                total_delivery_charge += price_obj.get('delivery_charge', 0) * cart.quantity
            else:
                total_delivery_charge += price_obj.get('delivery_charge', 0)
            total_selling_price += price_obj.get('selling_price', 0) * cart.quantity
            total_actual_price += price_obj.get('actual_price', 0) * cart.quantity
            total_discount += price_obj.get('discount', 0) * cart.quantity
        return {
            'delivery_charge': total_delivery_charge,
            'selling_price': total_selling_price,
            'actual_price': total_actual_price,
            'discount': total_discount
        }

    @staticmethod
    def total_amount_by_username(username: str):
        cart_data = Cart.objects.filter(user__username=username)
        total_amount = 0
        for data in cart_data:
            total_amount += data.get_total_price()
        return total_amount

    @staticmethod
    def total_discount_by_username(username: str):
        cart_data = Cart.objects.filter(user__username=username)
        total_discount = 0
        for data in cart_data:
            total_discount += data.get_total_discount()
        return total_discount

    @staticmethod
    def total_deliver_charge_by_username(username: str):
        return Cart.objects.filter(
            user__username=username
        ).aggregate(Sum('product__delivery_charge')).get('product__delivery_charge__sum', 0)
