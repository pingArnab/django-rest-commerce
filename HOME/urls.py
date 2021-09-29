from django.urls import path
from . import views


app_name = 'HOME'

# urls
urlpatterns = [
    path('', views.get_home, name='home'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('forget-password/', views.forgetPassword, name='forget-password'),
]
