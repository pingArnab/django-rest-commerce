import traceback

from django import template
from django.conf import settings
from django.template.defaultfilters import stringfilter

from TRANSACTION.models import Order

register = template.Library()


@register.filter
@stringfilter
def split_with(value: str, split_key):
    return value.split(split_key)


@register.filter
def data_at(value, index):
    return value[index]


@register.filter
def timespan_input(value):
    timespan = ''
    try:
        if int(value):
            timespan += '{}{}'.format(int(value), 'y')
        if round((value * 100) - (int(value) * 100)):
            timespan += '{}{}'.format(round((value * 100) - (int(value) * 100)), 'm')
        return timespan
    except Exception as e:
        return None


@register.filter
def get_final_price(order):
    try:
        return (order.get('actual_price') - order.get('discount')) * order.get('product_quantity')
    except Exception as e:
        traceback.print_exc()
        return None


@register.filter
def get_abs(value):
    return abs(value)


@register.filter
def date_to_year_month(number_of_days, t=None):
    if not number_of_days:
        return None
    years = number_of_days // 365
    months = (number_of_days - years * 365) // 30
    days = (number_of_days - years * 365 - months * 30)

    text = ''
    if years:
        text += f'{years}Years '
    if months:
        text += f'{months}Months '
    if days:
        text += f'{days}Days '

    if t == 'Y':
        return int(years)
    elif t == 'M':
        return int(months)
    elif t == 'D':
        return int(days)
    else:
        return text


@register.filter
def to_status_text(status_coded: str):
    status_dict = {
        Order.STATUS.PENDING_FOR_PAYMENT: 'Pending for Payment',
        Order.STATUS.PLACED: 'Waiting for packaging',
        Order.STATUS.READY_FOR_SHIPPING: 'Ready for Shipping',
        Order.STATUS.DISPATCHED: 'Dispatched',
        Order.STATUS.OUT_FOR_DELIVERY: 'Out for Delivery',
        Order.STATUS.DELIVERED: 'Delivered',
        Order.STATUS.REQUESTED_FOR_REFUND: 'Requested for Return',
        Order.STATUS.RETURNED: 'Returned',
    }
    return status_dict.get(status_coded.strip())


@register.filter
def status_color_badge(status_coded: str):
    status_dict = {
        Order.STATUS.PENDING_FOR_PAYMENT: 'p-2 badge badge-secondary',
        Order.STATUS.PLACED: 'p-2 badge badge-warning',
        Order.STATUS.READY_FOR_SHIPPING: 'p-2 badge badge-success',
        Order.STATUS.DISPATCHED: 'p-2 badge badge-primary',
        Order.STATUS.OUT_FOR_DELIVERY: 'p-2 badge badge-primary',
        Order.STATUS.DELIVERED: 'p-2 badge badge-primary',
        Order.STATUS.REQUESTED_FOR_REFUND: 'p-2 badge badge-danger',
        Order.STATUS.RETURNED: 'p-2 badge badge-danger',
    }
    return status_dict.get(status_coded.strip())


@register.simple_tag
def get_project_name():
    return settings.CONFIG.PROJECT_NAME
