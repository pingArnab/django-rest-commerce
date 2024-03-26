from django.contrib import admin
from django.urls import path
from . import api_views

app_name = 'SELLER.api'

# urls
urlpatterns = [
    path('products/', api_views.all_products_for_seller)
]