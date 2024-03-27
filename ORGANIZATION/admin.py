from django.contrib import admin
from .models import Organization, Permission

# Register your models here.
admin.site.register(Organization)
admin.site.register(Permission)
