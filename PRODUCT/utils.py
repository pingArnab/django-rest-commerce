from django.db.models import F
from django.db.models.query import QuerySet
from django.utils import timezone
from .models import Category, Product
from DRC.core.exceptions import DataNotFoundException


def product_filter_with_query_parameter(product_qs: QuerySet, query_params):
    category_id = query_params.get('category')
    sort_by = query_params.get('sortby')

    if category_id:
        if Category.objects.filter(category_id=category_id):
            product_qs = product_qs.filter(category=Category.objects.get(category_id=category_id))
        else:
            raise DataNotFoundException(Category, category_id, 'id')

    if sort_by:
        if str(sort_by).strip().lower() == 'release_date':
            product_qs = product_qs.order_by('-last_modified')
        elif str(sort_by).strip().lower() == 'discount_percentage':
            product_qs = product_qs.filter(
                offer=True,
                offer_end__gte=timezone.now().astimezone(),
                offer_start__lte=timezone.now().astimezone(),
            ).annotate(
                discount_percentage=(F('price') - F('offer_price')) / F('price') * 100
            ).order_by('-discount_percentage', '-rating', '-sell_count')

    return count_filter(product_qs, query_params.get('count'))


def count_filter(qs: QuerySet, count_param_data):
    try:
        count = int(count_param_data) if count_param_data else 0
    except:
        count = 0
    return qs[:count] if count >= 1 else qs
