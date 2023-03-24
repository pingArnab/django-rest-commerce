import logging
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.db.utils import IntegrityError
from django.http import Http404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from SELLER.models import Seller
from TRANSACTION import manager as transaction_manager
from PRODUCT.models import Product, Category
from DRC.core.DRCCommonUtil import AccessLevel, CTfiles
from TRANSACTION.models import Order
from DRC.settings import PROJECT_NAME

__module_name = f'{PROJECT_NAME}.' + __name__ + '::'
logger = logging.getLogger(__module_name)


# Create your views here.
@login_required(login_url='/login')
def get_seller_dashboard(request):
    order = transaction_manager.getSellerOrdersDict(request.user, 'UPDATES')
    order_list = list(order)[:100]

    new_order_stat, all_order_stat = transaction_manager.get_seller_order_stat(request.user)
    customer_stat = transaction_manager.get_seller_customer_stat(request.user)
    sales_stat = transaction_manager.get_seller_sales_stat(request.user)
    context = {
        'order_list': order_list,
        'cards': {
            'new_order_stat': new_order_stat,
            'all_order_stat': all_order_stat,
            'sales': sales_stat,
            'customer': customer_stat
        }
    }
    logger.debug(f"Seller Cards: {context.get('cards')}")
    # print(f"Seller Cards: {context.get('cards')}")
    return render(request, 'SELLER/dashboard.html', context)


def getSellerProductsPage(request):
    redirect_url = AccessLevel.checkAccess(request.user, allowed_access_level=AccessLevel.SELLER)
    if redirect_url:
        return redirect_url
    products = request.user.seller.product_set.values(
        'product_id', 'primary_image', 'product_name',
        'in_stock', 'price', 'offer_price', 'offer_end', 'in_stock',
        'sell_count', 'last_modified',
    ).all()
    # order_list = list(order)[:100]
    context = {
        'products': products.order_by('-last_modified'),
    }
    return render(request, 'SELLER/products-page.html', context)


def getOrderView(request, status: str, limit=None):
    redirect_url = AccessLevel.checkAccess(request.user, allowed_access_level=AccessLevel.SELLER)
    if redirect_url:
        return redirect_url

    if limit and (type(limit) is int):
        order_list = transaction_manager.getSellerOrdersDict(request.user, status)[:limit]
    else:
        order_list = transaction_manager.getSellerOrdersDict(request.user, status)
    context = {
        'order_list': order_list,
        'key': status,
    }
    logger.debug('::{} : {}'.format(__name__, order_list))
    return render(request, 'SELLER/orders-page.html', context)


def mark_order_ready_to_ship(request):
    redirect_url = AccessLevel.checkAccess(request.user, allowed_access_level=AccessLevel.SELLER)
    if redirect_url:
        return redirect_url
    if request.method == 'POST':
        return_to = request.POST.get('return-to') or 'SELLER:dashboard'
        order_id = request.POST.get('order_id')
        if Order.objects.filter(order_id=order_id):
            order = Order.objects.get(order_id=order_id)
            if order.order_status == Order.STATUS.PLACED and order.product.seller.user == request.user:
                order.order_status = Order.STATUS.READY_FOR_SHIPPING
                order.save()
            else:
                messages.error(request, 'Invalid request')
        else:
            messages.error(request, 'Invalid Order id')
        return redirect(return_to)
    else:
        raise Http404


def unmark_order_ready_to_ship(request):
    redirect_url = AccessLevel.checkAccess(request.user, allowed_access_level=AccessLevel.SELLER)
    if redirect_url:
        return redirect_url
    if request.method == 'POST':
        return_to = request.POST.get('return-to') or 'SELLER:dashboard'
        order_id = request.POST.get('order_id')
        if Order.objects.filter(order_id=order_id):
            order = Order.objects.get(order_id=order_id)
            if order.order_status == Order.STATUS.READY_FOR_SHIPPING and order.product.seller.user == request.user:
                order.order_status = Order.STATUS.PLACED
                order.save()
            else:
                messages.error(request, 'Invalid request')
        else:
            messages.error(request, 'Invalid Order id')
        return redirect(return_to)
    else:
        raise Http404


def add_product(request):
    FUNCTION_NAME = 'add_product'
    redirect_url = AccessLevel.checkAccess(request.user, allowed_access_level=AccessLevel.SELLER)
    if redirect_url:
        return redirect_url
    context = {
        'categories': Category.objects.all()
    }
    if request.method == 'POST':
        product = None
        try:
            product = Product.objects.create(

                product_name=request.POST.get('product-name'),
                price=request.POST.get('price'),
                delivery_charge=request.POST.get('delivery-charge') or 0,
                short_description=request.POST.get('short-description'),
                long_description=request.POST.get('long-description'),

                seller=request.user.seller,

                tag=request.POST.get('tag'),
                in_stock=request.POST.get('in_stock'),
                max_per_cart=request.POST.get('max_per_cart'),
                # warranty=request.POST.get('warranty') or 0,

                offer=True if request.POST.get('offer') else False,
                cod=True if request.POST.get('cod') else False,
            )
            for category in request.POST.getlist('category'):
                product.category.add(Category.objects.get(category_id=category))
            product.set_warranty(
                years=int(request.POST.get('warranty_years', 0)) if request.POST.get('warranty_years',
                                                                                     0).isdigit() else 0,
                months=int(request.POST.get('warranty_months', 0)) if request.POST.get('warranty_months',
                                                                                       0).isdigit() else 0,
                days=int(request.POST.get('warranty_days', 0)) if request.POST.get('warranty_days', 0).isdigit() else 0
            )
            # Save image in files - start
            primary_image_url = CTfiles.store(
                path=CTfiles.PRODUCT_PATH + product.product_id,
                file_data=request.FILES.get('primary-image')
            )
            product.primary_image = primary_image_url
            product.primary_image_placeholder = product.get_primary_image_thumbnail()
            logger.debug(FUNCTION_NAME + ' -> Saving file to: ' + str(primary_image_url))

            if request.FILES.get('optional-image-1'):
                optional_image_1_url = CTfiles.store(
                    path=CTfiles.PRODUCT_PATH + product.product_id,
                    file_data=request.FILES.get('optional-image-1')
                )
                product.optional_image_1 = optional_image_1_url
                logger.debug(FUNCTION_NAME + ' -> Saving file to: ' + str(optional_image_1_url))

            if request.FILES.get('optional-image-2'):
                optional_image_2_url = CTfiles.store(
                    path=CTfiles.PRODUCT_PATH + product.product_id,
                    file_data=request.FILES.get('optional-image-2')
                )
                product.optional_image_2 = optional_image_2_url
                logger.debug(FUNCTION_NAME + ' -> Saving file to: ' + str(optional_image_2_url))

            if request.FILES.get('optional-image-3'):
                optional_image_3_url = CTfiles.store(
                    path=CTfiles.PRODUCT_PATH + product.product_id,
                    file_data=request.FILES.get('optional-image-3')
                )
                product.optional_image_3 = optional_image_3_url
                logger.debug(FUNCTION_NAME + ' -> Saving file to: ' + str(optional_image_3_url))
            # Save image in files - end

            # adding product offer - start
            # print(request.POST.get('offer-start'))
            # raise Exception
            if product.offer:
                product.offer_price = request.POST.get('offer-price')
                product.offer_start = request.POST.get('offer-start')
                product.offer_end = request.POST.get('offer-end')

            product.save()
            logger.debug(FUNCTION_NAME + ' -> product saved: ' + str(product.product_id))
            messages.success(request, 'Product Added Successfully: ' + product.product_id)
            return redirect('SELLER:all-products')
        except IntegrityError as ie:
            if product:
                product.delete()
            logger.exception(FUNCTION_NAME + ' -> ' + str(ie))
            raise Http404('Please Mandatory fields !')
        except Exception as e:
            if product:
                product.delete()
            logger.exception(FUNCTION_NAME + ' -> ' + str(e))
            raise Http404('Unable to Process !')
    return render(request, 'SELLER/add-product.html', context)


def edit_product(request, product_id):
    FUNCTION_NAME = 'edit_product'
    redirect_url = AccessLevel.checkAccess(request.user, allowed_access_level=AccessLevel.SELLER)
    if redirect_url:
        return redirect_url

    if request.method == 'POST':

        if not Product.objects.filter(product_id=request.POST.get('product-id')):
            logger.error(FUNCTION_NAME + ' -> Product not exists {}'.format(request.POST.get('product-id')))
            raise Http404('Product not exists! '.format(request.POST.get('product-id')))

        product = Product.objects.get(product_id=request.POST.get('product-id'))

        product.product_name = request.POST.get('product-name')
        product.price = request.POST.get('price')
        product.delivery_charge = request.POST.get('delivery-charge')

        product.offer = bool(request.POST.get('offer-check'))
        product.offer_price = request.POST.get('offer-price')

        product.set_warranty(
            years=int(request.POST.get('warranty_years', 0)) if request.POST.get('warranty_years', 0).isdigit() else 0,
            months=int(request.POST.get('warranty_months', 0)) if request.POST.get('warranty_months',
                                                                                   0).isdigit() else 0,
            days=int(request.POST.get('warranty_days', 0)) if request.POST.get('warranty_days', 0).isdigit() else 0
        )
        if request.POST.get('offer-start'):
            product.offer_start = request.POST.get('offer-start')
        else:
            product.offer_start = None

        if request.POST.get('offer-end'):
            product.offer_end = request.POST.get('offer-end')
        else:
            product.offer_end = None

        if Category.objects.filter(category_id=request.POST.get('category')):
            # product.category = Category.objects.get(category_id=request.POST.get('category'))
            product.category.clear()
            for category in request.POST.getlist('category'):
                product.category.add(Category.objects.get(category_id=category))

        product.short_description = request.POST.get('short-description')
        product.long_description = request.POST.get('long-description')

        product.in_stock = request.POST.get('stock')
        product.max_per_cart = request.POST.get('max_per_cart')
        product.tag = request.POST.get('tag')
        product.cod = bool(request.POST.get('cod'))

        # Save image in files - start
        if request.FILES.get('primary-image'):
            primary_image_url = CTfiles.store(
                path=CTfiles.PRODUCT_PATH + product.product_id,
                file_data=request.FILES.get('primary-image')
            )
            product.primary_image = primary_image_url
            product.primary_image_placeholder = product.get_primary_image_thumbnail()

        if request.FILES.get('optional-image-1'):
            optional_image_1_url = CTfiles.store(
                path=CTfiles.PRODUCT_PATH + product.product_id,
                file_data=request.FILES.get('optional-image-1')
            )
            product.optional_image_1 = optional_image_1_url
            logger.debug(FUNCTION_NAME + ' -> Saving file to: ' + str(optional_image_1_url))

        if request.FILES.get('optional-image-2'):
            optional_image_2_url = CTfiles.store(
                path=CTfiles.PRODUCT_PATH + product.product_id,
                file_data=request.FILES.get('optional-image-2')
            )
            product.optional_image_2 = optional_image_2_url
            logger.debug(FUNCTION_NAME + ' -> Saving file to: ' + str(optional_image_2_url))

        if request.FILES.get('optional-image-3'):
            optional_image_3_url = CTfiles.store(
                path=CTfiles.PRODUCT_PATH + product.product_id,
                file_data=request.FILES.get('optional-image-3')
            )
            product.optional_image_3 = optional_image_3_url
            logger.debug(FUNCTION_NAME + ' -> Saving file to: ' + str(optional_image_3_url))
        # Save image in files - end

        product.save()
        messages.success(request, 'Product Updated Successfully: ' + product.product_id)
        return redirect('SELLER:all-products')
    context = {
        'categories': Category.objects.all()
    }
    # filesystem = FileSystemStorage()
    if Product.objects.filter(product_id=product_id):
        product = Product.objects.get(product_id=product_id)
        context['product'] = product
        return render(request, 'SELLER/edit-product.html', context)

    raise Http404


def delete_product(request, product_id):
    FUNCTION_NAME = 'delete_product'
    redirect_url = AccessLevel.checkAccess(request.user, allowed_access_level=AccessLevel.SELLER)
    if redirect_url:
        return redirect_url

    if not Product.objects.filter(product_id=product_id):
        logger.error(f'delete_product -> Product not exists {product_id}')
        messages.error(request, f'Product not found with product id: {product_id}')
        raise Http404(f'Product not exists! {product_id}')

    product = Product.objects.get(product_id=product_id)

    if not product.seller.user.username == request.user.username:
        logger.error(FUNCTION_NAME + ' -> Product not exists {}'.format(product_id))
        messages.error(request, 'Permission Denied !')
        raise Http404(f'Permission Denied! for product id: {product_id}')

    product.delete()
    messages.success(request, 'Product has been deleted with product id: ' + product_id)
    return redirect('SELLER:all-products')


# ------------------------   -----------------------------------
# ------------------------   -----------------------------------
# ------------------------API-----------------------------------
# ------------------------   -----------------------------------
# ------------------------   -----------------------------------
def getOrderData(request, status: str, limit=None):
    try:
        order = transaction_manager.getSellerOrdersDict(request.user, status)
        if limit and (type(limit) is int):
            order_list = list(order)[:limit]
        else:
            order_list = list(order)
        logger.debug('getOrderData : {}'.format(order_list))

        return JsonResponse({'order': order_list})
    except Exception as ex:
        logger.exception('getOrderData : {}'.format(ex))
        return JsonResponse({'status': 400})
