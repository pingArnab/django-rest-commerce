import datetime
import logging

from django.db.models import Sum, F
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.db.utils import IntegrityError
from django.http import Http404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User as AuthUser

from . import util
from .models import Seller
from MESSAGE.models import Message
from TRANSACTION import manager as transaction_manager
from PRODUCT.models import Product, Category
from DRC.core.DRCCommonUtil import AccessLevel, CTfiles, MONTH
from TRANSACTION.models import Order
from DRC.settings import PROJECT_NAME

__module_name = f'{PROJECT_NAME}.' + __name__ + '::'
logger = logging.getLogger(__module_name)


# Create your views here.
@login_required(login_url='/login')
def get_seller_dashboard(request):
    context = util.get_seller_context(request.user)

    order = transaction_manager.getSellerOrdersDict(request.user, 'UPDATES')
    order_list = list(order)[:100]

    new_order_stat, all_order_stat = transaction_manager.get_seller_order_stat(request.user)
    customer_stat = transaction_manager.get_seller_customer_stat(request.user)
    sales_stat = transaction_manager.get_seller_sales_stat(request.user)
    context.update({
        'order_list': order_list,
        'cards': {
            'new_order_stat': new_order_stat,
            'all_order_stat': all_order_stat,
            'sales': sales_stat,
            'customer': customer_stat
        }
    })
    logger.debug(f"Seller Cards: {context.get('cards')}")
    # print(f"Seller Cards: {context.get('cards')}")
    # print(f"__module_name: {__module_name}")
    return render(request, 'SELLER/dashboard.html', context)


@login_required(login_url='/login')
def getSellerProductsPage(request):
    context = util.get_seller_context(request.user)

    redirect_url = AccessLevel.checkAccess(request.user, allowed_access_level=AccessLevel.SELLER)
    if redirect_url:
        return redirect_url
    products = request.user.seller.product_set.values(
        'product_id', 'primary_image', 'product_name',
        'in_stock', 'price', 'offer_price', 'offer_end', 'in_stock',
        'sell_count', 'last_modified',
    ).all()
    # order_list = list(order)[:100]
    context['products'] = products.order_by('-last_modified')
    return render(request, 'SELLER/products-page.html', context)


@login_required(login_url='/login')
def get_order_view(request, status: str, limit=None):
    context = util.get_seller_context(request.user)

    redirect_url = AccessLevel.checkAccess(request.user, allowed_access_level=AccessLevel.SELLER)
    if redirect_url:
        return redirect_url

    if limit and (type(limit) is int):
        order_list = transaction_manager.getSellerOrdersDict(request.user, status)[:limit]
    else:
        order_list = transaction_manager.getSellerOrdersDict(request.user, status)
    context.update({
        'no_cancel_order_list': Order.NON_CANCELABLE_LIST,
        'order_list': order_list,
        'key': status,
    })
    logger.debug('::{} : {}'.format(__name__, order_list))
    return render(request, 'SELLER/orders-page.html', context)


@login_required(login_url='/login')
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


@login_required(login_url='/login')
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


@login_required(login_url='/login')
def add_product(request):
    FUNCTION_NAME = 'add_product'
    context = util.get_seller_context(request.user)
    redirect_url = AccessLevel.checkAccess(request.user, allowed_access_level=AccessLevel.SELLER)
    if redirect_url:
        return redirect_url
    context['categories'] = Category.objects.all()

    user: AuthUser = request.user
    unread_count = msg_list = Message.objects.filter(
        receiver=user, read_status=False
    ).count()
    context['unread_count'] = unread_count
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


@login_required(login_url='/login')
def edit_product(request, product_id):
    context = util.get_seller_context(request.user)
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
    context['categories'] = Category.objects.all()

    # filesystem = FileSystemStorage()
    if Product.objects.filter(product_id=product_id):
        product = Product.objects.get(product_id=product_id)
        context['product'] = product
        return render(request, 'SELLER/edit-product.html', context)

    raise Http404


@login_required(login_url='/login')
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


@login_required(login_url='/login')
def get_all_message(request):
    user: AuthUser = request.user
    context = util.get_seller_context(request.user)

    msg_list = Message.objects.filter(
        receiver=user
    ).order_by('-timestamp')
    context['messages_list'] = msg_list
    return render(request, 'SELLER/inbox.html', context)


@login_required(login_url='/login')
def get_message_by_id(request, message_id: str):
    FUNCTION_NAME = 'get_message_by_id()'
    context = {}

    user: AuthUser = request.user
    if not Message.objects.filter(message_id=message_id, receiver=user):
        logger.error(f'{FUNCTION_NAME}-> Message not exists {message_id}')
        messages.error(request, f'Message not found with message id: {message_id}')
        raise Http404(f'Message not exists! {message_id}')
    msg = Message.objects.get(message_id=message_id, receiver=user)
    if not msg.read_status:
        logger.debug(
            f'{FUNCTION_NAME} -> Seller: {user.get_full_name()}<{user.username}> is reading the message: {message_id}')
        msg.read_status = True
        msg.save()
    context['message'] = msg
    context.update(util.get_seller_context(user))
    return render(request, 'SELLER/message.html', context)


def cancel_order(request):
    FUNCTION_NAME = 'cancel_order'
    redirect_url = AccessLevel.checkAccess(request.user, allowed_access_level=AccessLevel.SELLER)
    if redirect_url:
        return redirect_url
    if request.method == 'POST':
        return_to = request.POST.get('return-to') or 'SELLER:dashboard'
        order_id = request.POST.get('order_id')
        seller_comment = request.POST.get('seller_comment')
        logger.debug(f'{FUNCTION_NAME}-> Canceled request received for Order: {order_id}')
        if Order.objects.filter(order_id=order_id):
            order = Order.objects.get(order_id=order_id)
            if order.order_status != Order.STATUS.CANCELED and order.product.seller.user == request.user:
                if order.order_status in Order.NON_CANCELABLE_LIST:
                    messages.error(request, f"This Order [order id: {order_id}] can't be canceled.")
                    return redirect(return_to)
                order.order_status = Order.STATUS.CANCELED
                order.created_at = datetime.datetime.now().astimezone()
                order.product.in_stock += order.product_quantity

                msg = Message.objects.create(
                    title=f'Order Canceled: {order_id}',
                    body=f'An order canceled by Seller with below comment: \n{seller_comment if seller_comment else ""}',
                    receiver=order.buyer,
                    sender=request.user,
                )
                msg.save()
                order.save()
                logger.debug(f'{FUNCTION_NAME}-> Order canceled: {order_id}')
            else:
                messages.error(request, 'Invalid request')
        else:
            messages.error(request, 'Invalid Order id')
        return redirect(return_to)
    else:
        raise Http404


# ------------------------   -----------------------------------
# ------------------------   -----------------------------------
# ------------------------API-----------------------------------
# ------------------------   -----------------------------------
# ------------------------   -----------------------------------
def getOrderData(request, status: str, limit=None):
    if not (request.user.is_authenticated and Seller.objects.filter(user=request.user)):
        return JsonResponse({'msg': "Unauthorised"}, status=401)
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


def get_yearly_sales_stats(request, sales_type: str = None, sales_range=None):
    FUNCTION_NAME = 'get_yearly_sales_stats'
    if not (request.user.is_authenticated and Seller.objects.filter(user=request.user)):
        return JsonResponse({'msg': "Unauthorised"}, status=401)
    try:
        if sales_type == 'year':
            year = sales_range or datetime.date.today().year
            desc = f'Sales for year: {year}'
            title = f'{year}'
            monthly_sales_report = Order.objects.filter(
                product__seller__user_id=request.user.id, placed_at__year=year,
                order_status__in=Order.POSITIVE_ORDER_STATUS
            ).values('placed_at__month').annotate(total_sale=Sum(F('actual_price') - F('discount')))
            monthly_sales_amount = []
            sales_month = []
            for sales in monthly_sales_report:
                monthly_sales_amount.append(sales.get('total_sale'))
                sales_month.append(MONTH.get_name(sales.get('placed_at__month')))
            if monthly_sales_amount and sales_month:
                monthly_sales_data = {'title': title, 'desc': desc, 'months': sales_month, 'amount': monthly_sales_amount}
            else:
                logger.exception(f'{FUNCTION_NAME} -> : monthly_sales_report for {year} = {monthly_sales_report}')
                return JsonResponse({'msg': f'No record found for {year}'}, status=404)
            logger.debug(f'{FUNCTION_NAME} -> monthly_sales_report = {monthly_sales_report}')
            return JsonResponse(monthly_sales_data)
        elif sales_type == 'month':
            month = sales_range or datetime.date.today().month
            year = datetime.date.today().year
            title = f'{MONTH.get_name(month)}, {year}'
            desc = f'Sales for {MONTH.get_short_name(month).upper()}-{year}'
            if month not in range(1, 13):
                return JsonResponse({'msg': 'Invalid Request: month must be in range of 1 to 12'}, status=400)
            monthly_sales_report = Order.objects.filter(
                product__seller__user_id=request.user.id,
                placed_at__month=month, placed_at__year=year,
                order_status__in=Order.POSITIVE_ORDER_STATUS
            ).values('placed_at__day').annotate(total_sale=Sum(F('actual_price') - F('discount')))
            daily_sales_amount = []
            sales_day = []
            for sales in monthly_sales_report:
                daily_sales_amount.append(sales.get('total_sale'))
                sales_day.append(f"{MONTH.get_short_name(month)} {sales.get('placed_at__day')}")
            if daily_sales_amount and sales_day:
                monthly_sales_data = {'title': title, 'desc': desc, 'days': sales_day, 'amount': daily_sales_amount}
            else:
                logger.exception(f'{FUNCTION_NAME} -> : monthly_sales_report for {year} = {monthly_sales_report}')
                return JsonResponse({'msg': f'No record found for {MONTH.get_name(month)}, {year}'}, status=404)
            logger.debug(f'{FUNCTION_NAME} -> monthly_sales_report = {monthly_sales_report}')
            return JsonResponse(monthly_sales_data)
        elif sales_type is None:
            seller_order = Order.objects.filter(
                product__seller__user_id=request.user.id,
                placed_at__month=datetime.date.today().month,
                placed_at__year=datetime.date.today().year
            )
            new = seller_order.filter(order_status=Order.STATUS.PLACED).count()
            processing = seller_order.filter(order_status__in=Order.ON_TRANSIT_ORDER_STATUS).count()
            delivered = seller_order.filter(order_status=Order.STATUS.DELIVERED).count()
            cancel = seller_order.filter(order_status=Order.STATUS.CANCELED).count()
            logger.debug(f'{FUNCTION_NAME} -> \nnew: {new} \nprocessing: {processing} \ndelivered: {delivered} \ncancel: {cancel}')
            return JsonResponse({
                'title': f'{MONTH.get_name(datetime.date.today().month)}, {datetime.date.today().year}',
                'month_year': f'{MONTH.get_short_name(datetime.date.today().month)}, {datetime.date.today().year}',
                'new': new, 'processing': processing, 'delivered': delivered, 'cancel': cancel
            })
        else:
            return JsonResponse({'msg': 'Invalid URL'}, status=400)

    except Exception as ex:
        logger.exception(f'{FUNCTION_NAME} -> : {ex.__str__()}')
        return JsonResponse({'msg': 'An Exception Occurred', 'details': ex.__str__()}, status=500)
