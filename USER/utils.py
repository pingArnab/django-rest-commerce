import json
import logging
from PRODUCT.models import Product
from .models import UserProfile
from django.contrib.auth.models import User
from django.contrib.auth import logout

__module_name = 'CTmela.' + __name__
logger = logging.getLogger(__module_name)


# Create your tests here.
def get_cart_product_data(username):
    try:
        userProfile = UserProfile.objects.get(user=User.objects.get(username=username))
        return userProfile.get_cart_view_product_details()
    except Exception as ex:
        logger.exception("Invalid User: <{username}>".format(username=username) + str(ex))
        return None


def get_cart_data(username):
    try:
        userProfile = UserProfile.objects.get(user=User.objects.get(username=username))
        return userProfile.get_cart()
    except Exception as ex:
        logger.exception("Invalid User: <{username}>".format(username=username) + str(ex))
        return None


def add_to_cart(username, product_id, count=1):
    try:
        userProfile = UserProfile.objects.get(user=User.objects.get(username=username))
        return userProfile.add_to_cart(product_id=product_id, count=count)
    except Exception as ex:
        logger.error("Invalid Cart Data: <{username}, {product_id}, {count}>".format(
            username=username,
            product_id=product_id,
            count=count
        ), ex)
        return {'status': 500, 'msg': 'Something went Wrong'}


def add_to_cart_batch(username, cart_products: dict):
    failure_count = 0
    for product_id, count in cart_products.items():
        res = add_to_cart(username, product_id, count)
        if res.get('status') == 200:
            failure_count += 1
        logger.debug("add_to_cart_batch :: added product in cart =>  Product: <{product_id}, {count}, status:{status}>".format(product_id=product_id, count=count, status=res.get('status')))
    return failure_count


def remove_from_cart(username, product_id):
    try:
        userProfile = UserProfile.objects.get(user=User.objects.get(username=username))
        userProfile.remove_from_cart(product_id=product_id)
        return True
    except Exception as ex:
        logger.error("Invalid Remove Request: <{username}, {product_id}>".format(
            username=username,
            product_id=product_id
        ), ex)
        return False


def set_cart(username, cart):
    try:
        userProfile = UserProfile.objects.get(user=User.objects.get(username=username))
        userProfile.set_cart(cart=cart)
        return True
    except Exception as ex:
        logger.exception("Invalid Cart Data: <{cart}>".format(cart=cart) + str(ex))
        return False


def clean_cart(username):
    try:
        userProfile = UserProfile.objects.get(user=User.objects.get(username=username))
        userProfile.clean_cart()
        return True
    except Exception as ex:
        logger.exception("Cart Cleaning Error <for User : {username}>".format(username=username) + str(ex))
        return False


def get_cookies_cart_data(cart_string):
    if cart_string:
        try:
            cart = json.loads(cart_string)
            dict(cart)
        except Exception as ex:
            logger.error('Cookies Cart: ' + str(ex))
            return '{}'
        product_list = list()
        for product_id, quantity in cart.items():
            try:
                product = Product.objects.get(product_id=product_id)
                product_dict = dict()
                product_dict['product_id'] = product.product_id
                product_dict['product_name'] = product.product_name
                product_dict['selling_price'] = product.get_price()['selling_price']
                product_dict['primary_image'] = product.get_primary_image_url()
                product_dict['quantity'] = quantity
                product_list.append(product_dict)
            except Exception as ex:
                logger.exception("{exception} \nProduct id = {product_id}>".format(product_id=product_id, exception=ex))
        return product_list
    else:
        return None


def add_to_cookies_cart(cart_string, product_id, product_count):
    try:
        quantity = int(product_count)
    except Exception as ex:
        logger.error('add_to_cookies_cart <Product Count Invalid: {}>'.format(product_count), ex)
        return [None, {'status': 500}]

    try:
        cart = json.loads(cart_string)
    except Exception as ex:
        logger.error('add_to_cookies_cart <Invalid Cart Data: {}>'.format(cart_string), ex)
        cart = {}

    try:
        product = Product.objects.get(product_id=product_id)
    except Exception as ex:
        logger.error("add_to_cookies_cart <Product id = {product_id}>".format(product_id=product_id), ex)
        return [None, {'status': 500}]

    if ((cart.get(product_id) or 0) + quantity) > product.max_per_cart:
        msg = 'Maximum no of item added'
        return [json.dumps(cart), {'status': 400, 'msg': msg}]
    elif cart.get(product_id):
        cart[product_id] += quantity
        msg = 'Product added to cart'
        return [json.dumps(cart), {'status': 200, 'msg': msg}]
    else:
        cart[product_id] = quantity
        msg = 'Product added to cart'
        return [json.dumps(cart), {'status': 200, 'msg': msg}]


def remove_from_cookies_cart(cart_string, product_id):
    try:
        cart = json.loads(cart_string)
    except Exception as ex:
        logger.error('remove_from_cookies_cart <Invalid Cart Data: {}>'.format(cart_string), ex)
        cart = {}
    logger.debug('remove_from_cookies_cart: before: ' + str(cart))
    if cart.get(product_id):
        del cart[product_id]
        logger.debug('remove_from_cookies_cart: after: ' + str(cart))
        return json.dumps(cart)
    else:
        logger.debug("remove_from_cookies_cart <Product id = {product_id}>".format(product_id=product_id))
        return json.dumps(cart)


def restrictAdmin(request):
    if request.user.is_authenticated:
        if request.user.is_superuser or request.user.is_staff:
            logout(request)
