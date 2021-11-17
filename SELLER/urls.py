from django.contrib import admin
from django.urls import path
from . import views

app_name = 'SELLER'

# urls
urlpatterns = [
    path('dashboard/', views.get_seller_dashboard, name='dashboard'),
    path('add-product/', views.add_product, name='add-product'),
    path('edit-product/<str:product_id>/', views.edit_product, name='edit-product'),
    path('delete-product/<str:product_id>/', views.delete_product, name='delete-product'),
    path('products/', views.getSellerProductsPage, name='all-products'),
    path('order/mark-order-ready-to-ship/', views.mark_order_ready_to_ship, name='mark-order-ready-to-ship'),
    path('order/unmark-order-ready-to-ship/', views.unmark_order_ready_to_ship, name='unmark-order-ready-to-ship'),
    path('api/orders/<str:status>/', views.getOrderData),
    path('api/orders/<str:status>/<int:limit>/', views.getOrderData),
    path('orders/<str:status>/', views.getOrderView, name='orders'),
    path('orders/<str:status>/<int:limit>/', views.getOrderView, name='orders-limit'),
]
