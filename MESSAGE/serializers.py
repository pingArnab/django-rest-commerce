import USER.models
from rest_framework import serializers
from .models import Message


class MessageListSerializer(serializers.ModelSerializer):
    receiver = serializers.SerializerMethodField()
    sender = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = (
            'message_id', 'title', 'body',
            'timestamp', 'receiver', 'read_status', 'sender'
        )

    @staticmethod
    def get_receiver(msg):
        return {
            'username': msg.receiver.username,
            'first_name': msg.receiver.first_name,
            'last_name': msg.receiver.last_name,
            'full_name': msg.receiver.get_full_name()
        }

    @staticmethod
    def get_sender(msg):
        return {
            'username': msg.sender.username,
            'first_name': msg.sender.first_name,
            'last_name': msg.sender.last_name,
            'full_name': msg.sender.get_full_name()
        }
