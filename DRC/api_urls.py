from django.urls import path
from PRODUCT import api_views as product_api_views
from HOME import api_views as home_api_views
from SELLER import api_views as seller_api_views
from USER import api_views as user_api_views
from TRANSACTION import api_views as transactions_api_views
from rest_framework_simplejwt import views as jwt_views
from MESSAGE import api_views as message_api_views
from . import customtokens

urlpatterns = [
    # JWT Token
    path('token/', customtokens.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', jwt_views.TokenVerifyView.as_view(), name='token_verify'),

    # User
    path('user/', user_api_views.user_profile),
    path('user/signup/', user_api_views.signup),
    path('user/verify/', user_api_views.verify_validation_key),
    path('user/verify/resend-mail/', user_api_views.resend_validation_key_email),
    path('user/address/', user_api_views.user_address),
    path('user/address/<str:address_id>/', user_api_views.user_address),
    path('user/wishlist/', user_api_views.user_wishlist),
    path('user/wishlist/<str:product_id>/', user_api_views.user_wishlist),
    path('user/cart/add-bulk/', user_api_views.add_all_user_cart),
    path('user/cart/', user_api_views.user_cart),
    path('user/cart/<str:product_id>/', user_api_views.user_cart),
    # User Message
    path('user/msgs/', message_api_views.all_msg_by_user),
    path('user/msgs/<str:status>/', message_api_views.all_msg_by_user),
    path('user/msg/<str:msg_id>/', message_api_views.msg_by_id),
    path('user/msg/<str:msg_id>/mark-as-read/', message_api_views.mark_msg_as_read),

    # Password
    path('user/password/', user_api_views.change_password),
    path('user/password/reset/', user_api_views.reset_password),

    # Orders
    path('user/orders/', transactions_api_views.all_orders),
    path('user/order/<str:order_id>/', transactions_api_views.order_by_id),
    path('user/order/<str:order_id>/cancel/', transactions_api_views.cancel_order_by_id),
    path('user/transaction/<str:transaction_id>/', transactions_api_views.transaction_by_id),
    path('user/transaction/<str:transaction_id>/', transactions_api_views.transaction_by_id),

    # Checkout
    path('checkout/pre-process/', transactions_api_views.checkout_pre_process),
    path('checkout/confirmation/', transactions_api_views.checkout_confirmation),

    # Seller
    path('seller/', seller_api_views.seller),
    path('seller/signup/', seller_api_views.seller_signup),

    # Hero
    path('heros/', home_api_views.get_all_heroes),

    # Products
    path('products/', product_api_views.all_products),
    path('product/<str:product_id>/', product_api_views.product_by_id),
    path('product/<str:product_id>/reviews/', product_api_views.reviews),
    path('product/<str:product_id>/review/', product_api_views.review),
    path('categories/', product_api_views.all_categories),

    path('search/', product_api_views.search),
    path('search-suggestion/', product_api_views.search_suggestion),

]
