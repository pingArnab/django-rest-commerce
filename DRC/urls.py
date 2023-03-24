from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.views.static import serve


urlpatterns = [
    path('admin/', admin.site.urls, name='ADMIN'),
    path('api/v1/', include('DRC.api_urls')),
    path('', include('HOME.urls')),
    path('seller/', include('SELLER.urls')),
    path('logs/', include('log_viewer.urls')),

    # Static and Media
    url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    url(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
]
