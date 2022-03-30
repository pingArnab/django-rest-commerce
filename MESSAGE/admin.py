from django.contrib import admin
from .models import Message


# Register your models here.
class MessageAdmin(admin.ModelAdmin):
    list_display = (
        'message_id', 'title', 'body',
        'timestamp', 'receiver', 'read_status', 'sender'
    )
    search_fields = [
        'message_id', 'title', 'body',
        'timestamp', 'receiver', 'read_status', 'sender'
    ]


admin.site.register(Message, MessageAdmin)
