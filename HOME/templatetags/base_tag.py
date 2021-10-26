from django import template
from django.template.defaultfilters import stringfilter, floatformat

register = template.Library()


@register.filter
@stringfilter
def b4_class(value: str):
    class_map = {
        'error': 'danger',
        'success': 'success',
        'warning': 'warning',
        'info': 'info',
        'debug': 'secondary',
    }
    return class_map.get(value.lower().strip()) or 'primary'


@register.simple_tag
def add(*values):
    return sum(values)


@register.filter
def add(value: int, carry: int):
    return value + carry
