from rest_framework import serializers
from core.models import ConversationMessage, ChatConversation


class ConversationMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConversationMessage
        fields = '__all__'


class ChatConversationSerializer(serializers.ModelSerializer):
    messages = ConversationMessageSerializer(many=True, required=False)

    class Meta:
        model = ChatConversation
        fields = '__all__'
